import contextlib
import os
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path

from pypdf import PdfReader

from resume_extractor.errors import (
    EXIT_INVALID_DOWNLOAD,
    EXIT_OUTPUT_PERMISSION,
    ExtractionError,
)

PERMISSION_GUIDANCE = (
    "grant your terminal app Files and Folders or Desktop access in "
    "System Settings > Privacy & Security"
)


def write_download_to_destination(
    save_fn: Callable[[Path], None], destination: Path
) -> Path:
    tmp: Path | None = None
    with convert_permission_error(destination):
        try:
            tmp = make_sibling_temp_file(destination)
            save_fn(tmp)
            validate_pdf_file(tmp)
            os.replace(tmp, destination)
            return destination
        except Exception:
            if tmp is not None:
                tmp.unlink(missing_ok=True)
            raise


@contextlib.contextmanager
def convert_permission_error(destination: Path) -> Iterator[None]:
    try:
        yield
    except PermissionError as e:
        raise ExtractionError(
            f"FAIL cannot write {destination}: {e}; {PERMISSION_GUIDANCE}",
            EXIT_OUTPUT_PERMISSION,
        )


def make_sibling_temp_file(destination: Path) -> Path:
    fd, name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    os.close(fd)
    return Path(name)


def validate_pdf_file(path: Path) -> None:
    try:
        page_count = len(PdfReader(str(path)).pages)
    except Exception as e:
        raise ExtractionError(
            f"FAIL download is not a readable pdf: {path} ({e})",
            EXIT_INVALID_DOWNLOAD,
        )
    if page_count < 1:
        raise ExtractionError(
            f"FAIL downloaded pdf has no pages: {path}", EXIT_INVALID_DOWNLOAD
        )
