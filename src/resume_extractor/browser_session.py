import subprocess
from pathlib import Path

from playwright.sync_api import BrowserContext, Playwright

from resume_extractor import config
from resume_extractor.errors import EXIT_BROWSER_NOT_INSTALLED, ExtractionError


def ensure_chromium_installed(playwright: Playwright) -> None:
    executable = Path(playwright.chromium.executable_path)
    if executable.exists():
        return
    print(f"INFO chromium missing at {executable}; running playwright.init")
    run_playwright_init()
    if not executable.exists():
        raise ExtractionError(
            f"FAIL chromium still missing at {executable}; "
            "run .venv/bin/python -m playwright install chromium",
            EXIT_BROWSER_NOT_INSTALLED,
        )


def run_playwright_init() -> None:
    try:
        result = subprocess.run(["playwright.init"], check=False)
    except FileNotFoundError:
        raise ExtractionError(
            "FAIL playwright.init is not on PATH; "
            "run .venv/bin/python -m playwright install chromium",
            EXIT_BROWSER_NOT_INSTALLED,
        )
    if result.returncode != 0:
        print(f"FAIL playwright.init exited with code {result.returncode}")


def launch_persistent_context(playwright: Playwright) -> BrowserContext:
    config.BROWSER_PROFILE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    return playwright.chromium.launch_persistent_context(
        str(config.BROWSER_PROFILE_DIR),
        headless=not config.INTERACTIVE,
        viewport={"width": 1280, "height": 900},
        accept_downloads=True,
    )
