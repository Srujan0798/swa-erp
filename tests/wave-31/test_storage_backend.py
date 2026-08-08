"""Wave 31 — storage backend tests (local + MinIO backends).

LocalStorage tests are pure unit tests. MinIOStorage tests and the MinIO API
round-trip require a live MinIO at the configured MINIO_ENDPOINT (default
``localhost:9000``, e.g. ``docker-compose up -d minio``); they skip cleanly when
it is not reachable so the suite stays green under a local-disk deployment.
"""
import json
import uuid

import pytest
from minio.error import S3Error
from urllib3.exceptions import MaxRetryError

from src.backend.core import storage as storage_module
from src.backend.core.config import settings
from src.backend.core.storage import LocalStorage, MinIOStorage, get_storage


def _minio_available() -> bool:
    try:
        MinIOStorage()
        return True
    except Exception:
        return False


requires_minio = pytest.mark.skipif(
    not _minio_available(), reason="MinIO not reachable at MINIO_ENDPOINT"
)


@pytest.fixture
def local_backend(tmp_path):
    return LocalStorage(root=tmp_path)


class TestLocalStorage:
    def test_save_read_roundtrip(self, local_backend):
        key = f"project-{uuid.uuid4()}/file.txt"
        stored = local_backend.save(key, b"hello local")
        assert stored == str(local_backend.root / key)
        assert (local_backend.root / key).read_bytes() == b"hello local"
        assert local_backend.read(key) == b"hello local"

    def test_save_returns_uploads_prefixed_path(self, tmp_path):
        backend = LocalStorage(root=tmp_path)
        stored = backend.save("boqs/1/one.json", b"{}")
        assert stored == str(tmp_path / "boqs/1/one.json")

    def test_read_accepts_stored_path_string(self, local_backend):
        stored = local_backend.save("a/b.bin", b"legacy")
        assert local_backend.read(stored) == b"legacy"

    def test_read_accepts_legacy_uploads_prefix(self, tmp_path):
        backend = LocalStorage(root=tmp_path)
        backend.save("sub/file.txt", b"data")
        legacy_path = str(tmp_path / "sub/file.txt")
        assert backend.read(legacy_path) == b"data"

    def test_delete_removes_file(self, local_backend):
        stored = local_backend.save("d/remove.txt", b"bye")
        local_backend.delete(stored)
        assert not (local_backend.root / "d/remove.txt").exists()

    def test_delete_missing_key_is_noop(self, local_backend):
        local_backend.delete("does/not/exist.txt")

    def test_url_returns_path(self, local_backend):
        local_backend.save("u/one.txt", b"x")
        assert local_backend.url("u/one.txt") == str(local_backend.root / "u/one.txt")

    def test_save_creates_nested_dirs(self, local_backend):
        stored = local_backend.save("nested/deep/dir.txt", b"x")
        assert (local_backend.root / "nested/deep/dir.txt").read_bytes() == b"x"
        assert stored == str(local_backend.root / "nested/deep/dir.txt")


@requires_minio
class TestMinIOStorage:
    def test_save_read_roundtrip(self):
        backend = MinIOStorage()
        key = f"test/wave31/{uuid.uuid4().hex}/bytes.bin"
        try:
            assert backend.save(key, b"hello minio") == key
            assert backend.read(key) == b"hello minio"
        finally:
            backend.delete(key)

    def test_save_read_binary_content(self):
        backend = MinIOStorage()
        key = f"test/wave31/{uuid.uuid4().hex}/payload.bin"
        payload = bytes(range(256))
        try:
            backend.save(key, payload)
            assert backend.read(key) == payload
        finally:
            backend.delete(key)

    def test_delete_removes_object(self):
        backend = MinIOStorage()
        key = f"test/wave31/{uuid.uuid4().hex}/gone.bin"
        backend.save(key, b"temp")
        backend.delete(key)
        with pytest.raises(S3Error):
            backend.read(key)

    def test_url_returns_presigned_link(self):
        backend = MinIOStorage()
        key = f"test/wave31/{uuid.uuid4().hex}/link.bin"
        try:
            backend.save(key, b"x")
            url = backend.url(key)
            assert url.startswith("http")
            assert key in url
        finally:
            backend.delete(key)


class TestGetStorageFactory:
    def test_default_is_local(self, monkeypatch):
        monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
        monkeypatch.setattr(storage_module, "_storage", None)
        assert isinstance(get_storage(), LocalStorage)

    @requires_minio
    def test_minio_backend_selected(self, monkeypatch):
        monkeypatch.setattr(settings, "STORAGE_BACKEND", "minio")
        monkeypatch.setattr(storage_module, "_storage", None)
        assert isinstance(get_storage(), MinIOStorage)

    def test_unknown_backend_raises(self, monkeypatch):
        monkeypatch.setattr(settings, "STORAGE_BACKEND", "nope")
        monkeypatch.setattr(storage_module, "_storage", None)
        with pytest.raises(ValueError):
            get_storage()


class TestMinIOFailsLoudly:
    def test_unreachable_endpoint_raises_on_init(self):
        with pytest.raises(MaxRetryError):
            MinIOStorage(endpoint="localhost:1")


class TestLocalApiRoundTrip:
    async def test_document_upload_download_byte_identical(
        self, authed_admin_client, test_project
    ):
        payload = b"wave-31 local round trip"
        upload = await authed_admin_client.post(
            f"/api/projects/{test_project.id}/documents",
            files={"file": ("roundtrip.txt", payload, "text/plain")},
        )
        assert upload.status_code == 201
        doc_id = upload.json()["id"]

        download = await authed_admin_client.get(f"/api/documents/{doc_id}/download")
        assert download.status_code == 200
        assert download.content == payload

    async def test_boq_upload_download_byte_identical(
        self, authed_admin_client, test_project
    ):
        payload = json.dumps(
            [
                {"description": "Item A", "unit": "nos", "quantity": 2, "rate": 100},
                {"description": "Item B", "unit": "sqm", "quantity": 5, "rate": 50},
            ]
        ).encode()
        upload = await authed_admin_client.post(
            f"/api/projects/{test_project.id}/boqs",
            files={"file": ("boq.json", payload, "application/json")},
        )
        assert upload.status_code == 201
        boq_id = upload.json()["id"]

        download = await authed_admin_client.get(f"/api/boqs/{boq_id}/download")
        assert download.status_code == 200
        assert download.content == payload


@requires_minio
class TestMinIOApiRoundTrip:
    async def test_document_upload_download_byte_identical(
        self, authed_admin_client, test_project, monkeypatch
    ):
        monkeypatch.setattr(settings, "STORAGE_BACKEND", "minio")
        monkeypatch.setattr(storage_module, "_storage", None)

        payload = b"wave-31 minio round trip"
        upload = await authed_admin_client.post(
            f"/api/projects/{test_project.id}/documents",
            files={"file": ("roundtrip.bin", payload, "application/octet-stream")},
        )
        assert upload.status_code == 201
        doc_id = upload.json()["id"]

        download = await authed_admin_client.get(f"/api/documents/{doc_id}/download")
        assert download.status_code == 200
        assert download.content == payload
