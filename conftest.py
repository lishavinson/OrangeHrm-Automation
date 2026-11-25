from base64 import b64encode
from collections.abc import Iterator
from pathlib import Path
import re

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidSessionIdException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from pytest_html import extras

from config.config import BASE_URL, BROWSER, TIMEOUT

PROJECT_ROOT = Path(__file__).resolve().parent


def pytest_configure(config: pytest.Config) -> None:
    (config.rootpath / "reports").mkdir(exist_ok=True)
    (config.rootpath / "screenshots").mkdir(exist_ok=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    safe_test_name = re.sub(r"[^A-Za-z0-9._-]+", "_", item.nodeid).strip("_")
    screenshot_path = PROJECT_ROOT / "screenshots" / f"{safe_test_name}.png"
    screenshot = driver.get_screenshot_as_png()
    screenshot_path.write_bytes(screenshot)

    report.extras = getattr(report, "extras", [])
    report.extras.append(
        extras.image(
            b64encode(screenshot).decode("ascii"),
            name="Failure screenshot",
        )
    )


@pytest.fixture
def driver() -> Iterator[WebDriver]:
    if BROWSER == "chrome":
        browser = webdriver.Chrome()
    elif BROWSER == "firefox":
        browser = webdriver.Firefox()
    else:
        raise ValueError(
            f"Unsupported BROWSER value: {BROWSER!r}. Use 'chrome' or 'firefox'."
        )

    try:
        browser.implicitly_wait(0)
        browser.get(f"{BASE_URL}/web/index.php/auth/login")
        WebDriverWait(browser, TIMEOUT).until(
            expected_conditions.visibility_of_element_located(
                (By.NAME, "username")
            )
        )
        yield browser
    finally:
        try:
            browser.quit()
        except InvalidSessionIdException:
            pass
