"""
Unified path management for the project.

All paths are absolute and relative to the project root directory.
This ensures the application works regardless of the startup directory.
"""

from pathlib import Path


# Project root directory (3 levels up from this file: utils -> backend -> src -> root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
TEXTBOOKS_DIR = DATA_DIR / "textbooks"
RUNTIME_DIR = DATA_DIR / "runtime"
JOBS_DIR = RUNTIME_DIR / "jobs"

# Report directory
REPORT_DIR = PROJECT_ROOT / "report"


def get_job_dir(job_id: str) -> Path:
    """
    Get the directory path for a specific job.

    Args:
        job_id: Job identifier

    Returns:
        Absolute path to the job directory
    """
    return JOBS_DIR / job_id


def ensure_directories():
    """
    Ensure all required directories exist.
    Creates them if they don't exist.
    """
    directories = [
        DATA_DIR,
        TEXTBOOKS_DIR,
        RUNTIME_DIR,
        JOBS_DIR,
        REPORT_DIR
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# Ensure directories exist on module import
ensure_directories()
