import re
import time
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import Download, Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from resume_extractor import config
from resume_extractor.errors import (
    EXIT_BROWSER_OR_NETWORK,
    EXIT_EXPORT_CONTROLS_MISSING,
    EXIT_INVALID_CREDENTIALS,
    EXIT_VERIFICATION_REQUIRED,
    ExtractionError,
)
from resume_extractor.pdf_output import write_download_to_destination


def classify_linkedin_page(url: str) -> str:
    path = urlsplit(url).path
    if "/checkpoint/" in path:
        return "checkpoint"
    if path.rstrip("/").endswith("/uas/login") or path.rstrip("/").endswith(
        "/login"
    ):
        return "login"
    if "/authwall" in path:
        return "authwall"
    if "/in/" in path:
        return "authenticated_profile"
    return "unknown"


def is_signin_wall_visible(page: Page) -> bool:
    if page.locator("[class*=authwall]").count() > 0:
        return True
    return (
        page.locator("main").get_by_role(
            "button", name=re.compile("^Sign in$")
        ).count()
        > 0
    )


def find_profile_resources_button(page: Page) -> Locator:
    return page.locator("main").get_by_role(
        "button", name=re.compile("Resources")
    )


def has_profile_resources_button(page: Page) -> bool:
    return find_profile_resources_button(page).count() > 0


def settle_page_state(page: Page, seconds: float = 10.0) -> str:
    deadline = time.monotonic() + seconds
    while True:
        state = classify_linkedin_page(page.url)
        if state != "authenticated_profile":
            return state
        if is_signin_wall_visible(page):
            return "authwall"
        if has_profile_resources_button(page):
            return state
        if time.monotonic() >= deadline:
            return state
        time.sleep(0.5)


def navigate_to_login_form(page: Page) -> None:
    sign_in_button = page.locator("main").get_by_role(
        "button", name=re.compile("^Sign in")
    )
    if sign_in_button.count() > 0:
        sign_in_button.first.click()
        page.wait_for_load_state("domcontentloaded")
    elif classify_linkedin_page(page.url) != "login":
        page.goto(config.LOGIN_URL, timeout=config.NAVIGATION_TIMEOUT_MS)
    page.locator(EMAIL_FIELD_SELECTOR).wait_for(state="visible", timeout=30_000)


EMAIL_FIELD_SELECTOR = "input#username:visible, input#session_key:visible"
PASSWORD_FIELD_SELECTOR = (
    "input#password:visible, input#session_password:visible"
)


def submit_single_login_attempt(page: Page, email: str, password: str) -> str:
    navigate_to_login_form(page)
    page.locator(EMAIL_FIELD_SELECTOR).first.fill(email)
    password_field = page.locator(PASSWORD_FIELD_SELECTOR).first
    password_field.fill(password)
    password_field.press("Enter")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)
    return classify_linkedin_page(page.url)


def raise_if_login_rejected(page: Page) -> None:
    for field in ("password", "username"):
        if page.locator(f"#error-for-{field}").first.is_visible():
            raise ExtractionError(
                "FAIL LinkedIn rejected the sign-in credentials",
                EXIT_INVALID_CREDENTIALS,
            )


def wait_for_checkpoint_to_clear(page: Page, seconds: int) -> str:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        state = classify_linkedin_page(page.url)
        if state != "checkpoint":
            return state
        time.sleep(config.CHECKPOINT_POLL_SECONDS)
    raise ExtractionError(
        f"FAIL verification checkpoint still active after {seconds}s",
        EXIT_VERIFICATION_REQUIRED,
    )


def verify_target_profile(page: Page) -> None:
    if config.TARGET_PROFILE_PATH not in urlsplit(page.url).path:
        raise ExtractionError(
            f"FAIL unexpected page after navigation: {page.url}",
            EXIT_BROWSER_OR_NETWORK,
        )
    name_element = page.locator("main").get_by_text(
        config.TARGET_PROFILE_NAME, exact=True
    ).first
    try:
        name_element.wait_for(state="visible", timeout=15_000)
    except PlaywrightTimeoutError:
        raise ExtractionError(
            f"FAIL profile does not show {config.TARGET_PROFILE_NAME} "
            f"at {page.url}",
            EXIT_BROWSER_OR_NETWORK,
        )
    if config.TARGET_PROFILE_NAME not in page.title():
        raise ExtractionError(
            f"FAIL page title does not name {config.TARGET_PROFILE_NAME}",
            EXIT_BROWSER_OR_NETWORK,
        )


def find_save_to_pdf_menu_item(page: Page) -> Locator:
    return page.get_by_role(
        "menuitem", name=re.compile("Save to PDF", re.IGNORECASE)
    )


def export_profile_pdf(page: Page) -> Download:
    resources = find_profile_resources_button(page)
    if resources.count() == 0:
        raise ExtractionError(
            "FAIL Resources button not found on profile",
            EXIT_EXPORT_CONTROLS_MISSING,
        )
    resources.first.click()
    save_item = find_save_to_pdf_menu_item(page)
    if save_item.count() == 0:
        raise ExtractionError(
            "FAIL Save to PDF item not found in Resources menu",
            EXIT_EXPORT_CONTROLS_MISSING,
        )
    with page.expect_download(timeout=config.DOWNLOAD_TIMEOUT_MS) as download_info:
        save_item.first.click()
    download = download_info.value
    failure = download.failure()
    if failure:
        raise ExtractionError(
            f"FAIL LinkedIn pdf download failed: {failure}",
            EXIT_BROWSER_OR_NETWORK,
        )
    return download


def save_downloaded_pdf(download: Download, destination: Path) -> None:
    write_download_to_destination(download.save_as, destination)
