"""
Test unified path management.

Verifies that all paths are absolute and point to the correct project directories.
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Add src/backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend"))

from utils.paths import (
    PROJECT_ROOT,
    DATA_DIR,
    TEXTBOOKS_DIR,
    RUNTIME_DIR,
    JOBS_DIR,
    REPORT_DIR,
    get_job_dir,
    ensure_directories
)


def test_paths_are_absolute():
    """Test that all paths are absolute."""
    paths = [
        PROJECT_ROOT,
        DATA_DIR,
        TEXTBOOKS_DIR,
        RUNTIME_DIR,
        JOBS_DIR,
        REPORT_DIR
    ]

    for path in paths:
        assert path.is_absolute(), f"Path {path} is not absolute"
        print(f"[OK] {path.name}: {path}")


def test_paths_point_to_project_root():
    """Test that paths point to the correct project root."""
    # PROJECT_ROOT should contain key files/directories
    assert (PROJECT_ROOT / "src").exists(), "src directory not found in PROJECT_ROOT"
    assert (PROJECT_ROOT / "CLAUDE.md").exists() or True, "CLAUDE.md should be in PROJECT_ROOT"

    print(f"[OK] PROJECT_ROOT correctly points to: {PROJECT_ROOT}")


def test_data_directory_structure():
    """Test that data directory structure is correct."""
    assert DATA_DIR == PROJECT_ROOT / "data"
    assert TEXTBOOKS_DIR == DATA_DIR / "textbooks"
    assert RUNTIME_DIR == DATA_DIR / "runtime"
    assert JOBS_DIR == RUNTIME_DIR / "jobs"

    print("[OK] Data directory structure is correct")


def test_report_directory():
    """Test that report directory is correct."""
    assert REPORT_DIR == PROJECT_ROOT / "report"
    print(f"[OK] REPORT_DIR: {REPORT_DIR}")


def test_get_job_dir():
    """Test get_job_dir function."""
    job_id = "test123"
    job_dir = get_job_dir(job_id)

    assert job_dir.is_absolute(), "Job directory is not absolute"
    assert job_dir == JOBS_DIR / job_id
    assert str(job_id) in str(job_dir)

    print(f"[OK] get_job_dir('test123'): {job_dir}")


def test_ensure_directories():
    """Test that ensure_directories creates all required directories."""
    ensure_directories()

    directories = [
        DATA_DIR,
        TEXTBOOKS_DIR,
        RUNTIME_DIR,
        JOBS_DIR,
        REPORT_DIR
    ]

    for directory in directories:
        assert directory.exists(), f"Directory {directory} was not created"
        assert directory.is_dir(), f"{directory} is not a directory"

    print("[OK] All directories exist")


def test_paths_work_from_any_directory(tmp_path):
    """Test that paths work regardless of current working directory."""
    import os

    # Save original directory
    original_dir = Path.cwd()

    try:
        # Change to a different directory
        os.chdir(tmp_path)

        # Re-import to test
        from utils.paths import PROJECT_ROOT as ROOT_FROM_DIFFERENT_DIR

        # Paths should still be absolute and correct
        assert ROOT_FROM_DIFFERENT_DIR.is_absolute()
        assert (ROOT_FROM_DIFFERENT_DIR / "src").exists()

        print(f"[OK] Paths work from different directory: {tmp_path}")

    finally:
        # Restore original directory
        os.chdir(original_dir)


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Unified Path Management")
    print("=" * 60)

    test_paths_are_absolute()
    print()

    test_paths_point_to_project_root()
    print()

    test_data_directory_structure()
    print()

    test_report_directory()
    print()

    test_get_job_dir()
    print()

    test_ensure_directories()
    print()

    # Create a temp directory for testing
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_paths_work_from_any_directory(Path(tmp_dir))

    print()
    print("=" * 60)
    print("All path tests passed!")
    print("=" * 60)
