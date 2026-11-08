from pathlib import Path

INTERACTIVE: bool = False
DEBUG: bool = False

STATE_DIR = (
    Path.home()
    / "Library"
    / "Application Support"
    / "resume_extractor_from_linkedin"
)
BROWSER_PROFILE_DIR = STATE_DIR / "browser_profile"
LOCK_FILE = STATE_DIR / "run.lock"
CREDENTIALS_FILE = Path.home() / ".linkedin"
PROFILE_URL = "https://www.linkedin.com/in/nelson-sproul/"
LOGIN_URL = "https://www.linkedin.com/login"
DEFAULT_OUTPUT = Path.home() / "Desktop" / "Nelson-Sproul-Resume.pdf"
NAVIGATION_TIMEOUT_MS = 45_000
DOWNLOAD_TIMEOUT_MS = 90_000
CHECKPOINT_DEFAULT_SECONDS = 300
CHECKPOINT_POLL_SECONDS = 2
TARGET_PROFILE_PATH = "/in/nelson-sproul"
TARGET_PROFILE_NAME = "Nelson Sproul"
