import argparse
import sys
from pathlib import Path

import playwright.sync_api
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from resume_extractor import browser_session, config, credentials, linkedin
from resume_extractor.errors import (
    EXIT_BROWSER_OR_NETWORK,
    EXIT_USAGE,
    EXIT_VERIFICATION_REQUIRED,
    ExtractionError,
)
from resume_extractor.process_lock import hold_run_lock


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="extract_resume",
        description="Export the LinkedIn profile as a pdf.",
    )
    parser.add_argument("--email", default=None)
    parser.add_argument(
        "--output", default=str(config.DEFAULT_OUTPUT)
    )
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument(
        "--checkpoint-seconds",
        type=int,
        default=config.CHECKPOINT_DEFAULT_SECONDS,
    )
    return parser.parse_args(argv)


def run_extraction(email: str | None, destination: Path, checkpoint_seconds: int) -> None:
    with playwright.sync_api.sync_playwright() as pw:
        browser_session.ensure_chromium_installed(pw)
        context = browser_session.launch_persistent_context(pw)
        try:
            page = context.new_page()
            open_profile_and_authenticate(page, email, checkpoint_seconds)
            linkedin.verify_target_profile(page)
            download = linkedin.export_profile_pdf(page)
            linkedin.save_downloaded_pdf(download, destination)
            print(f"OK saved {destination}")
        finally:
            context.close()


def open_profile_and_authenticate(
    page: Page, email: str | None, checkpoint_seconds: int
) -> None:
    page.goto(config.PROFILE_URL, timeout=config.NAVIGATION_TIMEOUT_MS)
    state = linkedin.settle_page_state(page)
    if config.DEBUG:
        print(f"INFO initial page state: {state} ({page.url})")
    if state == "authenticated_profile":
        return
    if state == "checkpoint":
        resolve_checkpoint(page, checkpoint_seconds)
        return
    perform_login_flow(page, email, checkpoint_seconds)


def perform_login_flow(
    page: Page, email: str | None, checkpoint_seconds: int
) -> None:
    if not email:
        raise ExtractionError(
            "FAIL sign-in is required; pass --email you@example.com",
            EXIT_USAGE,
        )
    password = credentials.read_linkedin_password()
    state = linkedin.submit_single_login_attempt(page, email, password)
    if config.DEBUG:
        print(f"INFO page state after login: {state} ({page.url})")
    linkedin.raise_if_login_rejected(page)
    if state == "checkpoint":
        resolve_checkpoint(page, checkpoint_seconds)
        return
    if state == "login":
        raise ExtractionError(
            f"FAIL still on sign-in page after login attempt ({page.url})",
            EXIT_BROWSER_OR_NETWORK,
        )
    page.goto(config.PROFILE_URL, timeout=config.NAVIGATION_TIMEOUT_MS)


def resolve_checkpoint(page: Page, checkpoint_seconds: int) -> None:
    if not config.INTERACTIVE:
        raise ExtractionError(
            "FAIL LinkedIn requests manual verification; "
            "re-run with --interactive to complete it in the browser",
            EXIT_VERIFICATION_REQUIRED,
        )
    print("INFO checkpoint shown; complete it in the browser window")
    state = linkedin.wait_for_checkpoint_to_clear(page, checkpoint_seconds)
    if state != "authenticated_profile":
        page.goto(config.PROFILE_URL, timeout=config.NAVIGATION_TIMEOUT_MS)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config.INTERACTIVE = args.interactive
    config.DEBUG = args.debug
    destination = Path(args.output).expanduser().resolve()
    try:
        with hold_run_lock():
            run_extraction(args.email, destination, args.checkpoint_seconds)
    except ExtractionError as e:
        print(str(e), file=sys.stderr)
        return e.exit_code
    except PlaywrightError as e:
        print(f"FAIL browser error: {e}", file=sys.stderr)
        return EXIT_BROWSER_OR_NETWORK
    except OSError as e:
        print(f"FAIL system error: {e}", file=sys.stderr)
        return EXIT_BROWSER_OR_NETWORK
    return 0
