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

    def _ensure_under_root(self, path: Path) -> Path:
        root = self.root.resolve()
        candidate = path.resolve()
        try:
            candidate.relative_to(root)
        except ValueError as e:
            raise ValueError("storage key escapes upload root") from e
        return path

    def _path(self, key: str) -> Path:
        """Map a key or legacy stored path onto a location under ``root``.

        Relative keys are joined under root. Absolute keys / paths that already
        start with the root prefix (legacy ``save`` return values like
        ``uploads/foo``) are accepted only when they resolve under root. Any
        path that escapes root (including ``..`` traversal) is rejected.
        """
        raw = Path(key)
        if raw.is_absolute() or str(raw).startswith(str(self.root)):
            return self._ensure_under_root(raw)
        return self._ensure_under_root(self.root / raw)

    def save(self, key: str, content: bytes) -> str:
        if Path(key).is_absolute():
            raise ValueError("absolute storage keys are not allowed")
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return str(self.root / key)

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
