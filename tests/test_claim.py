import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config.config import TIMEOUT
from pages.claim_page import ClaimPage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from test_data.login_data import VALID_PASSWORD, VALID_USERNAME


@pytest.fixture
def claim_page(driver: WebDriver) -> ClaimPage:
    LoginPage(driver).login(VALID_USERNAME, VALID_PASSWORD)
    WebDriverWait(driver, TIMEOUT).until(
        expected_conditions.url_contains("/dashboard/index")
    )
    DashboardPage(driver).navigate_to_module("Claim")
    page = ClaimPage(driver)
    page.wait_until_loaded()
    return page


@pytest.mark.claim
@pytest.mark.smoke
def test_claim_employee_list_is_displayed(claim_page: ClaimPage) -> None:
    assert claim_page.get_text(claim_page.employee_claims_heading) == "Employee Claims"


@pytest.mark.claim
@pytest.mark.regression
def test_claim_filters_can_be_reset(claim_page: ClaimPage) -> None:
    claim_page.select_filter_option("Status", "Submitted")
    claim_page.select_filter_option("Include", "Past Employees Only")

    assert claim_page.get_filter_value("Status") == "Submitted"
    assert claim_page.get_filter_value("Include") == "Past Employees Only"

    claim_page.reset_claim_filters()

    assert claim_page.get_filter_value("Status") == "-- Select --"
    assert claim_page.get_filter_value("Include") == "-- Select --"


@pytest.mark.claim
@pytest.mark.regression
def test_claim_request_requires_event_and_currency(
    claim_page: ClaimPage,
) -> None:
    claim_page.open_submit_claim()
    claim_page.create_claim_request()

    assert claim_page.get_validation_errors().count("Required") == 2
