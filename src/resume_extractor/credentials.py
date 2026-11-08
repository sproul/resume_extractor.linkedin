from pathlib import Path

from resume_extractor import config
from resume_extractor.errors import EXIT_USAGE, ExtractionError


def read_linkedin_password(path: Path = config.CREDENTIALS_FILE) -> str:
    if not path.is_file():
        raise ExtractionError(
            f"FAIL credentials file missing: {path}; "
            "store the LinkedIn password there and run chmod 600 on it",
            EXIT_USAGE,
        )
    enforce_owner_only_permissions(path)
    return read_single_line_secret(path)


def enforce_owner_only_permissions(path: Path) -> None:
    mode = path.stat().st_mode & 0o777
    if mode != 0o600:
        raise ExtractionError(
            f"FAIL {path} has mode {mode:03o}; run chmod 600 {path}", EXIT_USAGE
        )


def read_single_line_secret(path: Path) -> str:
    content = path.read_bytes().decode("utf-8").rstrip("\n")
    if not content:
        raise ExtractionError(f"FAIL credentials file is empty: {path}", EXIT_USAGE)
    if "\n" in content:
        raise ExtractionError(
            f"FAIL credentials file must contain exactly one line: {path}",
            EXIT_USAGE,
        )
    return content
