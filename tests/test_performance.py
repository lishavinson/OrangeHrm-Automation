from collections.abc import Iterator

import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config.config import BASE_URL, TIMEOUT
from pages.admin_page import AdminPage, AdminSubcategoryFormPage
from pages.login_page import LoginPage
from pages.performance_page import PerformancePage
from test_data.login_data import VALID_PASSWORD, VALID_USERNAME
from test_data.performance_data import create_kpi_name


PERFORMANCE_NAVIGATION_DESTINATIONS = [
    pytest.param(
        "Configure",
        [
            ("KPIs", "/performance/searchKpi", "Key Performance Indicators for Job Title"),
            ("Trackers", "/performance/viewPerformanceTracker", "Performance Trackers"),
        ],
        id="configure",
    ),
    pytest.param(
        "Manage Reviews",
        [
            ("Manage Reviews", "/performance/searchPerformanceReview", "Manage Performance Reviews"),
            ("My Reviews", "/performance/myPerformanceReview", "My Reviews"),
            ("Employee Reviews", "/performance/searchEvaluatePerformanceReview", "Employee Reviews"),
        ],
        id="manage-reviews",
    ),
]

PERFORMANCE_DIRECT_DESTINATIONS = [
    pytest.param(
        "My Trackers",
        "/performance/viewMyPerformanceTrackerList",
        "My Performance Trackers",
        id="my-trackers",
    ),
    pytest.param(
        "Employee Trackers",
        "/performance/viewEmployeePerformanceTrackerList",
        "Employee Performance Trackers",
        id="employee-trackers",
    ),
]


@pytest.fixture
def performance_page(driver: WebDriver) -> PerformancePage:
    LoginPage(driver).login(VALID_USERNAME, VALID_PASSWORD)
    WebDriverWait(driver, TIMEOUT).until(
        expected_conditions.url_contains("/dashboard/index")
    )
    page = PerformancePage(driver)
    page.open_performance_module()
    return page


def _open_job_titles_page(driver: WebDriver) -> AdminSubcategoryFormPage:
    driver.get(f"{BASE_URL}/web/index.php/admin/viewSystemUsers")
    admin_page = AdminPage(driver)
    admin_page.wait_until_loaded()
    admin_page.open_subcategory("Job", "Job Titles", "Job Titles")
    page = AdminSubcategoryFormPage(driver, "Job Titles")
    page.wait_until_loaded()
    return page


@pytest.fixture
def kpi_record(
    performance_page: PerformancePage,
) -> Iterator[tuple[PerformancePage, str, str]]:
    driver = performance_page.driver
    kpi_name = create_kpi_name()
    created_job_title: str | None = None
    kpi_save_attempted = False
    try:
        performance_page.open_submenu_item("Configure", "KPIs")
        performance_page.open_kpi_add_form()

        job_title = performance_page.select_first_available_job_title()
        if job_title is None:
            job_title_to_create = create_kpi_name(
                "Automation KPI Job Title"
            )

            job_titles_page = _open_job_titles_page(driver)
            job_titles_page.open_add_form()
            job_titles_page.set_field("Job Title", job_title_to_create)
            job_titles_page.save_form(job_title_to_create)
            created_job_title = job_title_to_create

            performance_page.open_performance_module()
            performance_page.open_submenu_item("Configure", "KPIs")
            performance_page.open_kpi_add_form()
            performance_page.select_job_title(job_title_to_create)
            job_title = job_title_to_create

        performance_page.set_kpi_field("Key Performance Indicator", kpi_name)
        kpi_save_attempted = True
        performance_page.save_kpi_form()

        yield performance_page, kpi_name, job_title
    finally:
        if kpi_save_attempted:
            driver.get(f"{BASE_URL}/web/index.php/performance/searchKpi")
            performance_page.wait_until_kpi_list_loaded()
            if performance_page.has_kpi_record(kpi_name):
                performance_page.delete_kpi_record(kpi_name)
        if created_job_title is not None:
            job_titles_page = _open_job_titles_page(driver)
            job_titles_page.wait.until(
                lambda _: job_titles_page.has_record(created_job_title)
            )
            job_titles_page.delete_record(created_job_title)


@pytest.mark.performance
@pytest.mark.smoke
def test_performance_module_is_displayed(
    performance_page: PerformancePage,
) -> None:
    assert performance_page.is_heading_visible("Performance")
    assert performance_page.is_heading_visible("Employee Reviews")


@pytest.mark.performance
@pytest.mark.smoke
@pytest.mark.parametrize(
    ("category", "destinations"),
    PERFORMANCE_NAVIGATION_DESTINATIONS,
)
def test_performance_category_navigation(
    performance_page: PerformancePage,
    category: str,
    destinations: list[tuple[str, str, str]],
) -> None:
    for item, route_fragment, heading in destinations:
        performance_page.open_submenu_item(category, item)

        assert route_fragment in performance_page.driver.current_url
        assert performance_page.is_heading_visible(heading)


@pytest.mark.performance
@pytest.mark.regression
@pytest.mark.parametrize(
    ("item", "route_fragment", "heading"),
    PERFORMANCE_DIRECT_DESTINATIONS,
)
def test_performance_trackers_navigation(
    performance_page: PerformancePage,
    item: str,
    route_fragment: str,
    heading: str,
) -> None:
    performance_page.open_submenu_item("Trackers", item)

    assert route_fragment in performance_page.driver.current_url
    assert performance_page.is_heading_visible(heading)


@pytest.mark.performance
@pytest.mark.smoke
def test_kpi_list_is_displayed(performance_page: PerformancePage) -> None:
    performance_page.open_submenu_item("Configure", "KPIs")

    assert performance_page.is_heading_visible(
        "Key Performance Indicators for Job Title"
    )


@pytest.mark.performance
@pytest.mark.smoke
def test_add_kpi_form_is_displayed(performance_page: PerformancePage) -> None:
    performance_page.open_submenu_item("Configure", "KPIs")
    performance_page.open_kpi_add_form()

    assert performance_page.is_heading_visible("Add Key Performance Indicator")


@pytest.mark.performance
@pytest.mark.regression
def test_add_kpi_requires_job_title_and_name(
    performance_page: PerformancePage,
) -> None:
    performance_page.open_submenu_item("Configure", "KPIs")
    performance_page.open_kpi_add_form()
    performance_page.submit_invalid_kpi_form()

    assert "Required" in performance_page.get_validation_errors()


@pytest.mark.performance
@pytest.mark.smoke
def test_create_kpi(
    kpi_record: tuple[PerformancePage, str, str],
) -> None:
    performance_page, kpi_name, _ = kpi_record

    assert performance_page.has_kpi_record(kpi_name)


@pytest.mark.performance
@pytest.mark.regression
def test_search_kpis_by_job_title(
    kpi_record: tuple[PerformancePage, str, str],
) -> None:
    performance_page, kpi_name, job_title = kpi_record
    performance_page.open_submenu_item("Configure", "KPIs")
    performance_page.search_kpis_by_job_title(job_title)

    assert performance_page.has_kpi_record(kpi_name)


@pytest.mark.performance
@pytest.mark.regression
def test_reset_kpi_search(
    kpi_record: tuple[PerformancePage, str, str],
) -> None:
    performance_page, _, job_title = kpi_record
    performance_page.open_submenu_item("Configure", "KPIs")
    performance_page.search_kpis_by_job_title(job_title)
    performance_page.reset_kpi_search()

    assert performance_page.get_selected_job_title() == "-- Select --"


@pytest.mark.performance
@pytest.mark.regression
def test_edit_kpi(
    kpi_record: tuple[PerformancePage, str, str],
) -> None:
    performance_page, kpi_name, _ = kpi_record
    performance_page.open_submenu_item("Configure", "KPIs")
    performance_page.open_edit_kpi_form(kpi_name)

    edited_name = create_kpi_name("Edited Automation KPI")
    performance_page.set_kpi_field("Key Performance Indicator", edited_name)
    performance_page.save_kpi_form()

    assert performance_page.has_kpi_record(edited_name)
    performance_page.delete_kpi_record(edited_name)


@pytest.mark.performance
@pytest.mark.smoke
def test_delete_kpi(
    kpi_record: tuple[PerformancePage, str, str],
) -> None:
    performance_page, kpi_name, _ = kpi_record
    performance_page.open_submenu_item("Configure", "KPIs")
    performance_page.delete_kpi_record(kpi_name)

    assert not performance_page.has_kpi_record(kpi_name)
