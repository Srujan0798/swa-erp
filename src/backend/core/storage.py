from __future__ import annotations

import io
from pathlib import Path
from typing import Protocol

from src.backend.core.config import settings

UPLOAD_ROOT = Path("uploads")


class StorageBackend(Protocol):
    def save(self, key: str, content: bytes) -> str:
        """Persist content at ``key`` and return the stored path/URL."""
        ...

    def read(self, key: str) -> bytes:
        """Return the bytes previously stored at ``key`` (or a stored path)."""
        ...

    def delete(self, key: str) -> None:
        """Remove the object at ``key``. No-op if it does not exist."""
        ...

    def url(self, key: str) -> str:
        """Return a URL/locator that can be used to fetch the stored object."""
        ...


class LocalStorage:
    """Filesystem backend wrapping the historical ``uploads/<key>`` layout.

    ``save`` returns a ``uploads/...``-prefixed relative path, matching the
    value services have always persisted in ``file_path`` columns. ``read``,
    ``delete`` and ``url`` additionally accept bare keys (paths under the
    root) so the same calls work against either backend.
    """

    def __init__(self, root: Path | str = UPLOAD_ROOT) -> None:
        self.root = Path(root)

    def _path(self, key: str) -> Path:
        path = Path(key)
        if path.is_absolute() or str(path).startswith(str(self.root)):
            return path
        return self.root / path

    def save(self, key: str, content: bytes) -> str:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return str(path)

    def read(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def delete(self, key: str) -> None:
        path = self._path(key)
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    def url(self, key: str) -> str:
        return str(self._path(key))


class MinIOStorage:
    """S3-compatible object storage backend (MinIO) via the ``minio`` client.

    Connection failure at construction raises immediately — a misconfigured or
    unreachable MinIO must not silently fall back to local disk.
    """

    def __init__(
        self,
        endpoint: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket: str | None = None,
        secure: bool = False,
    ) -> None:
        from minio import Minio

        self.bucket = bucket or settings.MINIO_BUCKET
        self.client = Minio(
            endpoint or settings.MINIO_ENDPOINT,
            access_key=access_key or settings.MINIO_ACCESS_KEY,
            secret_key=secret_key or settings.MINIO_SECRET_KEY,
            secure=secure or settings.MINIO_SECURE,
        )
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def save(self, key: str, content: bytes) -> str:
        self.client.put_object(
            self.bucket,
            key,
            io.BytesIO(content),
            length=len(content),
        )
        return key

    def read(self, key: str) -> bytes:
        response = self.client.get_object(self.bucket, key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def delete(self, key: str) -> None:
        self.client.remove_object(self.bucket, key)

    def url(self, key: str) -> str:
        return self.client.presigned_get_object(self.bucket, key)


_storage: StorageBackend | None = None


def get_storage() -> StorageBackend:
    """Return the configured storage backend, built once at first use."""
    global _storage
    if _storage is None:
        backend = settings.STORAGE_BACKEND.strip().lower()
        if backend == "minio":
            _storage = MinIOStorage()
        elif backend == "local":
            _storage = LocalStorage()
        else:
            msg = f"Unknown STORAGE_BACKEND: {settings.STORAGE_BACKEND!r}. Use 'local' or 'minio'."
            raise ValueError(msg)
    return _storage
