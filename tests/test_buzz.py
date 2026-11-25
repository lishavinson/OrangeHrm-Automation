import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config.config import TIMEOUT
from pages.buzz_page import BuzzPage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from test_data.login_data import VALID_PASSWORD, VALID_USERNAME


@pytest.fixture
def buzz_page(driver: WebDriver) -> BuzzPage:
    LoginPage(driver).login(VALID_USERNAME, VALID_PASSWORD)
    WebDriverWait(driver, TIMEOUT).until(
        expected_conditions.url_contains("/dashboard/index")
    )
    DashboardPage(driver).navigate_to_module("Buzz")
    page = BuzzPage(driver)
    page.wait_until_loaded()
    return page


@pytest.mark.buzz
@pytest.mark.smoke
def test_buzz_page_is_displayed(buzz_page: BuzzPage) -> None:
    assert buzz_page.get_text(buzz_page.buzz_heading) == "Buzz"


@pytest.mark.buzz
@pytest.mark.regression
@pytest.mark.parametrize(
    "filter_name",
    [
        "Most Recent Posts",
        "Most Liked Posts",
        "Most Commented Posts",
    ],
)
def test_buzz_feed_filter_can_be_selected(
    buzz_page: BuzzPage,
    filter_name: str,
) -> None:
    buzz_page.select_feed_filter(filter_name)

    assert buzz_page.get_active_feed_filter() == filter_name


@pytest.mark.buzz
@pytest.mark.regression
def test_buzz_post_text_can_be_entered_without_submitting(
    buzz_page: BuzzPage,
) -> None:
    post_text = "Automation post draft"
    buzz_page.set_post_text(post_text)

    assert buzz_page.get_post_text() == post_text
