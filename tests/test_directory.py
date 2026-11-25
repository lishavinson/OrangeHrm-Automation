import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config.config import TIMEOUT
from pages.dashboard_page import DashboardPage
from pages.directory_page import DirectoryPage
from pages.login_page import LoginPage
from test_data.login_data import VALID_PASSWORD, VALID_USERNAME


@pytest.fixture
def directory_page(driver: WebDriver) -> DirectoryPage:
    LoginPage(driver).login(VALID_USERNAME, VALID_PASSWORD)
    WebDriverWait(driver, TIMEOUT).until(
        expected_conditions.url_contains("/dashboard/index")
    )
    DashboardPage(driver).navigate_to_module("Directory")
    page = DirectoryPage(driver)
    page.wait_until_loaded()
    return page


@pytest.mark.directory
@pytest.mark.smoke
def test_directory_page_is_displayed(directory_page: DirectoryPage) -> None:
    assert directory_page.get_text(directory_page.directory_heading) == "Directory"


@pytest.mark.directory
@pytest.mark.regression
def test_directory_search_displays_results_or_empty_state(
    directory_page: DirectoryPage,
) -> None:
    result_count = directory_page.search_directory()

    assert result_count > 0 or directory_page.is_no_records_message_displayed()


@pytest.mark.directory
@pytest.mark.regression
def test_directory_dropdown_filters_can_be_reset(
    directory_page: DirectoryPage,
) -> None:
    job_title = next(
        (
            option
            for option in directory_page.get_filter_options("Job Title")
            if option != "-- Select --"
        ),
        None,
    )
    location = next(
        (
            option
            for option in directory_page.get_filter_options("Location")
            if option != "-- Select --"
        ),
        None,
    )

    if job_title is not None:
        directory_page.select_filter_option("Job Title", job_title)
    if location is not None:
        directory_page.select_filter_option("Location", location)

    directory_page.reset_filters()

    assert directory_page.get_filter_value("Job Title") == "-- Select --"
    assert directory_page.get_filter_value("Location") == "-- Select --"
