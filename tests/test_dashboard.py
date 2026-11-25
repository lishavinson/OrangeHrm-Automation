import pytest
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config.config import TIMEOUT
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from test_data.dashboard_data import DASHBOARD_MODULES, PROFILE_MENU_ITEMS
from test_data.login_data import VALID_PASSWORD, VALID_USERNAME


@pytest.fixture
def dashboard_page(driver):
    login_page = LoginPage(driver)
    login_page.login(VALID_USERNAME, VALID_PASSWORD)
    WebDriverWait(driver, TIMEOUT).until(
        expected_conditions.url_contains("/dashboard/index")
    )

    page = DashboardPage(driver)
    page.wait_until_loaded()
    return page


@pytest.mark.dashboard
@pytest.mark.smoke
def test_TC_DASH_001_dashboard_is_displayed_after_login(dashboard_page, driver):
    assert "/dashboard/index" in driver.current_url
    assert dashboard_page.is_sidebar_visible()


@pytest.mark.dashboard
@pytest.mark.smoke
def test_TC_DASH_002_dashboard_heading(dashboard_page):
    assert dashboard_page.get_heading() == "Dashboard"


@pytest.mark.dashboard
@pytest.mark.smoke
def test_TC_DASH_003_navigation_menu(dashboard_page):
    assert dashboard_page.get_sidebar_module_names() == DASHBOARD_MODULES


@pytest.mark.dashboard
@pytest.mark.regression
def test_user_profile_menu_shows_options(dashboard_page):
    dashboard_page.open_profile_menu()

    assert dashboard_page.get_profile_menu_items() == PROFILE_MENU_ITEMS


@pytest.mark.dashboard
@pytest.mark.regression
def test_TC_DASH_004_pim_employee_management_navigation(
    dashboard_page,
    driver,
) -> None:
    expected_route = dashboard_page.navigate_to_module("PIM")

    assert expected_route in driver.current_url


@pytest.mark.dashboard
@pytest.mark.regression
def test_TC_DASH_005_leave_navigation(dashboard_page, driver) -> None:
    expected_route = dashboard_page.navigate_to_module("Leave")

    assert expected_route in driver.current_url


@pytest.mark.dashboard
@pytest.mark.regression
def test_TC_DASH_006_recruitment_navigation(dashboard_page, driver) -> None:
    expected_route = dashboard_page.navigate_to_module("Recruitment")

    assert expected_route in driver.current_url


@pytest.mark.dashboard
@pytest.mark.regression
def test_sidebar_navigates_to_all_other_modules(dashboard_page, driver) -> None:
    highlighted_modules = {"PIM", "Leave", "Recruitment"}
    navigation_order = [
        module_name
        for module_name in DASHBOARD_MODULES
        if module_name not in highlighted_modules | {"Maintenance"}
    ]
    navigation_order.append("Maintenance")

    for module_name in navigation_order:
        expected_route = dashboard_page.navigate_to_module(module_name)
        assert expected_route in driver.current_url
