import io
import os
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfWriter

from resume_extractor import errors
from resume_extractor.pdf_output import write_download_to_destination


def tiny_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


class WriteDownloadToDestinationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.destination = Path(self.temp_dir.name) / "resume.pdf"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def leftover_temp_files(self) -> list[Path]:
        return [p for p in Path(self.temp_dir.name).iterdir() if p.name.startswith(".")]

    def test_valid_pdf_replaces_destination(self) -> None:
        write_download_to_destination(
            lambda p: p.write_bytes(tiny_pdf_bytes()), self.destination
        )
        self.assertTrue(self.destination.read_bytes().startswith(b"%PDF"))
        self.assertEqual([], self.leftover_temp_files())

    def test_non_pdf_bytes_fail_and_preserve_existing_destination(self) -> None:
        original = tiny_pdf_bytes()
        self.destination.write_bytes(original)
        with self.assertRaises(errors.ExtractionError) as caught:
            write_download_to_destination(
                lambda p: p.write_bytes(b"not a pdf"), self.destination
            )
        self.assertEqual(errors.EXIT_INVALID_DOWNLOAD, caught.exception.exit_code)
        self.assertEqual(original, self.destination.read_bytes())
        self.assertEqual([], self.leftover_temp_files())

    def test_save_fn_failure_preserves_destination_and_cleans_up(self) -> None:
        original = tiny_pdf_bytes()
        self.destination.write_bytes(original)

        def failing_save(path: Path) -> None:
            raise RuntimeError("download failed")

        with self.assertRaises(RuntimeError):
            write_download_to_destination(failing_save, self.destination)
        self.assertEqual(original, self.destination.read_bytes())
        self.assertEqual([], self.leftover_temp_files())

    def test_read_only_destination_dir_gives_exit_10(self) -> None:
        if os.geteuid() == 0:
            self.skipTest("root can write anywhere")
        readonly = Path(self.temp_dir.name) / "readonly"
        readonly.mkdir()
        readonly.chmod(0o500)
        with self.assertRaises(errors.ExtractionError) as caught:
            write_download_to_destination(
                lambda p: p.write_bytes(tiny_pdf_bytes()),
                readonly / "resume.pdf",
            )
        self.assertEqual(errors.EXIT_OUTPUT_PERMISSION, caught.exception.exit_code)
        readonly.chmod(0o700)

    def test_empty_pdf_is_rejected(self) -> None:
        writer = PdfWriter()
        buffer = io.BytesIO()
        writer.write(buffer)
        empty_pdf = buffer.getvalue()
        with self.assertRaises(errors.ExtractionError) as caught:
            write_download_to_destination(
                lambda p: p.write_bytes(empty_pdf), self.destination
            )
        self.assertEqual(errors.EXIT_INVALID_DOWNLOAD, caught.exception.exit_code)


if __name__ == "__main__":
    unittest.main()
