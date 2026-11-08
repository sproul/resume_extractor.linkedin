import os
import tempfile
import unittest
from pathlib import Path

from resume_extractor import errors
from resume_extractor.credentials import read_linkedin_password


class CredentialsTest(unittest.TestCase):
    def make_file(self, content: bytes, mode: int = 0o600) -> Path:
        fd, name = tempfile.mkstemp()
        os.write(fd, content)
        os.close(fd)
        path = Path(name)
        path.chmod(mode)
        self.addCleanup(path.unlink)
        return path

    def test_reads_password_and_strips_trailing_newlines(self) -> None:
        path = self.make_file(b"s3cret\n\n")
        self.assertEqual("s3cret", read_linkedin_password(path))

    def test_empty_file_is_fatal(self) -> None:
        path = self.make_file(b"")
        with self.assertRaises(errors.ExtractionError) as caught:
            read_linkedin_password(path)
        self.assertEqual(errors.EXIT_USAGE, caught.exception.exit_code)

    def test_only_newlines_is_fatal(self) -> None:
        path = self.make_file(b"\n\n")
        with self.assertRaises(errors.ExtractionError) as caught:
            read_linkedin_password(path)
        self.assertEqual(errors.EXIT_USAGE, caught.exception.exit_code)

    def test_embedded_newline_is_fatal(self) -> None:
        path = self.make_file(b"one\ntwo\n")
        with self.assertRaises(errors.ExtractionError) as caught:
            read_linkedin_password(path)
        self.assertEqual(errors.EXIT_USAGE, caught.exception.exit_code)

    def test_world_readable_mode_is_fatal(self) -> None:
        path = self.make_file(b"s3cret", mode=0o644)
        with self.assertRaises(errors.ExtractionError) as caught:
            read_linkedin_password(path)
        self.assertEqual(errors.EXIT_USAGE, caught.exception.exit_code)
        self.assertIn("chmod 600", str(caught.exception))

    def test_missing_file_is_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "nope"
            with self.assertRaises(errors.ExtractionError) as caught:
                read_linkedin_password(missing)
            self.assertEqual(errors.EXIT_USAGE, caught.exception.exit_code)


if __name__ == "__main__":
    unittest.main()
