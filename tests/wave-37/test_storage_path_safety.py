"""Wave-37 — LocalStorage path traversal guards."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.backend.core.storage import LocalStorage


def test_save_and_read_roundtrip(tmp_path: Path) -> None:
    store = LocalStorage(root=tmp_path / "uploads")
    saved = store.save("docs/a.txt", b"hello")
    assert "a.txt" in saved
    assert store.read("docs/a.txt") == b"hello"


def test_rejects_parent_traversal(tmp_path: Path) -> None:
    store = LocalStorage(root=tmp_path / "uploads")
    with pytest.raises(ValueError, match="escapes"):
        store.save("../escape.txt", b"nope")


def test_rejects_absolute_key_on_save(tmp_path: Path) -> None:
    store = LocalStorage(root=tmp_path / "uploads")
    with pytest.raises(ValueError, match="absolute"):
        store.save("/tmp/evil.txt", b"nope")
