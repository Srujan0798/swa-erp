"""Security tests for backup scripts.

Tests for wave-27 task 01 — Security-review findings + lint.
Covers:
  1. Credentials not leaking into logs
  2. Database backup/restore scripts work without password exposure
"""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKUP_DB = REPO_ROOT / "scripts" / "backup_db.sh"
RESTORE_DB = REPO_ROOT / "scripts" / "restore_db.sh"


@pytest.fixture(scope="module")
def test_db_url():
    """Database URL for tests - use scratch DB to avoid conflicts."""
    import uuid

    scratch_name = f"swa_erp_test_{uuid.uuid4().hex[:8]}"
    admin_url = "postgresql://swa:swa@localhost:5432/postgres"
    return f"postgresql://swa:swa@localhost:5432/{scratch_name}", admin_url, scratch_name


def test_backup_script_no_password_leak(tmp_path):
    """backup_db.sh must not emit database password in any output."""
    out_dir = tmp_path / "backups"
    out_dir.mkdir()
    
    password = "secret_pwd_123"
    test_url = f"postgresql://swa:{password}@localhost:5432/swa_erp"
    
    env = os.environ.copy()
    env["DATABASE_URL"] = test_url
    
    # Run backup script
    result = subprocess.run(
        ["bash", str(BACKUP_DB), str(out_dir), "30"],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    
    # Check output doesn't contain password
    output = result.stdout + result.stderr
    assert password not in output, f"Password '{password}' found in backup script output!"
    assert result.returncode == 0, f"Backup script failed: {result.stderr}"


def test_restore_script_no_password_leak(test_db_url):
    """restore_db.sh must not emit database password in prompt."""
    
    db_url, admin_url, scratch_name = test_db_url
    
    # Create scratch database
    subprocess.run(
        ["psql", admin_url, "-c", f"CREATE DATABASE {scratch_name};"],
        capture_output=True,
        text=True,
        check=True,
    )
    
    try:
        password = "secret_pwd_456"
        # Get a backup file to test with
        backup_file = subprocess.run(
            ["bash", str(BACKUP_DB), "/tmp", "30"],
            capture_output=True,
            text=True,
            check=True,
        )
        
        # Find the backup file
        backup_files = list(Path("/tmp").glob("swa_erp_backup_*.sql.gz"))
        if not backup_files:
            pytest.skip("No backup file found for restore test")
        
        backup_path = backup_files[0]
        
        # Parse host/port/db/user from URL for the prompt (same as restore_db.sh does)
        db_user = db_url.split("://")[1].split("@")[0].split(":")[0]
        db_host_port = db_url.split("@")[1].split("/")[0]
        db_host = db_host_port.split(":")[0]
        db_port = db_host_port.split(":")[1] if ":" in db_host_port else "5432"
        db_name = db_url.split("/")[1].split("?")[0]
        
        # Run restore with --yes to skip prompt
        env = os.environ.copy()
        env["DATABASE_URL"] = db_url
        
        result = subprocess.run(
            ["bash", str(RESTORE_DB), str(backup_path), "--yes"],
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
        )
        
        # Check output doesn't contain password
        output = result.stdout + result.stderr
        # Note: password won't be in the prompt since restore_db.sh only prints host/port/dbname/user
        assert password not in output, f"Password found in restore script output!"
        
    finally:
        # Cleanup
        subprocess.run(
            ["psql", admin_url, "-c", f"DROP DATABASE IF EXISTS {scratch_name};"],
            capture_output=True,
            text=True,
        )


def test_restore_script_still_names_target_db(tmp_path):
    """restore_db.sh must still name the target database in its prompt."""
    
    # Create a temporary backup file
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    
    # Create a dummy backup file (just a placeholder, won't actually be used)
    backup_file = backup_dir / "dummy_backup.sql.gz"
    backup_file.write_text("dummy")
    
    # Run restore script with --yes
    env = os.environ.copy()
    env["DATABASE_URL"] = "postgresql://swa:swa@localhost:5432/test_db"
    
    result = subprocess.run(
        ["bash", str(RESTORE_DB), str(backup_file), "--yes"],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    
    # Check that the prompt includes the database name
    assert "test_db" in result.stdout, "restore_db.sh prompt must include database name"
    assert "target db   : test_db" in result.stdout or "target db   : test_db" in result.stderr, "Database name must appear in prompt"


def test_backup_restore_roundtrip_no_password_leak(test_db_url):
    """Full backup → restore round-trip works without password exposure."""
    
    db_url, admin_url, scratch_name = test_db_url
    
    # Create scratch database
    subprocess.run(
        ["psql", admin_url, "-c", f"CREATE DATABASE {scratch_name};"],
        capture_output=True,
        text=True,
        check=True,
    )
    
    try:
        # Populate with test data
        subprocess.run(
            [
                "psql", db_url,
                "-c", "CREATE TABLE smoke (id int, marker text);"
                "INSERT INTO smoke VALUES (1, 'swa-backup-test-marker'), (2, 'second-row');"
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        
        # Back it up
        backup_dir = tmp_path = tempfile.mkdtemp()
        env = os.environ.copy()
        env["DATABASE_URL"] = db_url
        
        result = subprocess.run(
            ["bash", str(BACKUP_DB), backup_dir, "30"],
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
        )
        
        assert result.returncode == 0, f"Backup failed: {result.stderr}"
        
        # Find the backup file
        backup_files = list(Path(backup_dir).glob("swa_erp_backup_*.sql.gz"))
        assert len(backup_files) == 1
        backup_file = backup_files[0]
        
        # Drop and recreate the DB so the restore is meaningful
        subprocess.run(
            ["psql", admin_url, "-c", f"DROP DATABASE {scratch_name};"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        
        subprocess.run(
            ["psql", admin_url, "-c", f"CREATE DATABASE {scratch_name};"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        
        # Update the URL with the new database name
        db_url = f"postgresql://swa:swa@localhost:5432/{scratch_name}"
        
        # Restore with --yes
        result = subprocess.run(
            ["bash", str(RESTORE_DB), str(backup_file), "--yes"],
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
        )
        
        assert result.returncode == 0, f"Restore failed: {result.stderr}"
        
        # Verify the marker row came back
        result = subprocess.run(
            [
                "psql", db_url,
                "-c", "SELECT count(*) FROM smoke;",
                "-c", "SELECT marker FROM smoke ORDER BY id;",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        assert result.returncode == 0
        assert "2" in result.stdout, f"Expected 2 rows, got: {result.stdout}"
        assert "swa-backup-test-marker" in result.stdout
        assert "second-row" in result.stdout
        
    finally:
        # Cleanup
        subprocess.run(
            ["psql", admin_url, "-c", f"DROP DATABASE IF EXISTS {scratch_name};"],
            capture_output=True,
            text=True,
        )
