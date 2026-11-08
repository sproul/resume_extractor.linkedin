import contextlib
import fcntl
import os
from collections.abc import Iterator
from pathlib import Path

from resume_extractor import config
from resume_extractor.errors import EXIT_LOCK_HELD, ExtractionError


@contextlib.contextmanager
def hold_run_lock(lock_path: Path = config.LOCK_FILE) -> Iterator[None]:
    lock_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise ExtractionError(
                f"FAIL another extraction is already running (lock {lock_path})",
                EXIT_LOCK_HELD,
            )
        yield
    finally:
        os.close(fd)
