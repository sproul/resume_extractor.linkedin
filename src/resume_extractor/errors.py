EXIT_OK = 0
EXIT_USAGE = 2
EXIT_INVALID_CREDENTIALS = 3
EXIT_VERIFICATION_REQUIRED = 4
EXIT_EXPORT_CONTROLS_MISSING = 5
EXIT_BROWSER_OR_NETWORK = 6
EXIT_INVALID_DOWNLOAD = 7
EXIT_LOCK_HELD = 8
EXIT_BROWSER_NOT_INSTALLED = 9
EXIT_OUTPUT_PERMISSION = 10


class ExtractionError(Exception):
    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code
