import tempfile
import unittest
from pathlib import Path

from resume_extractor import errors
from resume_extractor.process_lock import hold_run_lock


class RunLockTest(unittest.TestCase):
    def test_second_acquire_fails_while_held_and_succeeds_after_release(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            lock_path = Path(temp_dir) / "run.lock"
            with hold_run_lock(lock_path):
                with self.assertRaises(errors.ExtractionError) as caught:
                    with hold_run_lock(lock_path):
                        pass
                self.assertEqual(errors.EXIT_LOCK_HELD, caught.exception.exit_code)
            with hold_run_lock(lock_path):
                pass
            self.assertEqual(0o600, lock_path.stat().st_mode & 0o777)


if __name__ == "__main__":
    unittest.main()
