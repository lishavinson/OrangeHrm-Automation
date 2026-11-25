import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config.config import TIMEOUT
from pages.login_page import LoginPage
from pages.time_page import TimePage
from test_data.login_data import VALID_PASSWORD, VALID_USERNAME


@pytest.fixture
def time_page(driver: WebDriver) -> TimePage:
    LoginPage(driver).login(VALID_USERNAME, VALID_PASSWORD)
    WebDriverWait(driver, TIMEOUT).until(
        expected_conditions.url_contains("/dashboard/index")
    )
    page = TimePage(driver)
    page.open_time_module()
    return page


TIME_NAVIGATION_DESTINATIONS = [
    pytest.param(
        "Timesheets",
        [
            ("My Timesheets", "/time/viewMyTimesheet", "My Timesheet"),
            (
                "Employee Timesheets",
                "/time/viewEmployeeTimesheet",
                "Select Employee",
            ),
        ],
        id="timesheets",
    ),
    pytest.param(
        "Attendance",
        [
            (
                "My Records",
                "/attendance/viewMyAttendanceRecord",
                "My Attendance Records",
            ),
            ("Punch In/Out", "/attendance/punchIn", "Punch In"),
            (
                "Employee Records",
                "/attendance/viewAttendanceRecord",
                "Employee Attendance Records",
            ),
            (
                "Configuration",
                "/attendance/configure",
                "Attendance Configuration",
            ),
        ],
        id="attendance",
    ),
    pytest.param(
        "Reports",
        [
            (
                "Project Reports",
                "/time/displayProjectReportCriteria",
                "Project Report",
            ),
            (
                "Employee Reports",
                "/time/displayEmployeeReportCriteria",
                "Employee Report",
            ),
            (
                "Attendance Summary",
                "/time/displayAttendanceSummaryReportCriteria",
                "Attendance Total Summary Report",
            ),
        ],
        id="reports",
    ),
    pytest.param(
        "Project Info",
        [
            ("Customers", "/time/viewCustomers", "Customers"),
            ("Projects", "/time/viewProjects", "Projects"),
        ],
        id="project-info",
    ),
]


@pytest.mark.time
@pytest.mark.smoke
@pytest.mark.parametrize(
    ("category", "destinations"),
    TIME_NAVIGATION_DESTINATIONS,
)
def test_time_category_dropdown_navigation(
    time_page: TimePage,
    category: str,
    destinations: list[tuple[str, str, str]],
) -> None:
    for item, route_fragment, heading in destinations:
        time_page.open_submenu_item(category, item)

        assert route_fragment in time_page.driver.current_url
        assert time_page.is_heading_visible(heading)


@pytest.mark.time
@pytest.mark.regression
def test_employee_timesheet_search_requires_employee_name(
    time_page: TimePage,
) -> None:
    time_page.view_employee_timesheet()

    assert "Required" in time_page.get_validation_errors()


@pytest.mark.time
@pytest.mark.regression
def test_employee_timesheet_can_be_opened_by_employee_name(
    time_page: TimePage,
) -> None:
    time_page.open_submenu_item("Timesheets", "Employee Timesheets")
    employee_names = time_page.get_pending_timesheet_employee_names()
    if not employee_names:
        pytest.skip("No pending timesheets are available for an employee search.")

    employee_name = employee_names[0]
    time_page.set_employee_name_filter(employee_name)
    time_page.select_employee_suggestion(employee_name)
    time_page.view_employee_timesheet()

    assert "/time/viewTimesheet/employeeId/" in time_page.driver.current_url
    assert time_page.get_timesheet_detail_heading().startswith("Timesheet for ")


@pytest.mark.time
@pytest.mark.regression
def test_my_timesheet_period_control_is_displayed(time_page: TimePage) -> None:
    time_page.open_submenu_item("Timesheets", "My Timesheets")

    assert time_page.is_my_timesheet_period_visible()


@pytest.mark.time
@pytest.mark.regression
def test_punch_in_form_is_displayed_without_submitting(
    time_page: TimePage,
) -> None:
    time_page.open_submenu_item("Attendance", "Punch In/Out")

    assert time_page.is_punch_in_form_visible()


@pytest.mark.time
@pytest.mark.regression
def test_employee_attendance_search_form_is_displayed(
    time_page: TimePage,
) -> None:
    time_page.open_submenu_item("Attendance", "Employee Records")

    assert time_page.is_employee_attendance_search_form_visible()


@pytest.mark.time
@pytest.mark.regression
def test_project_report_requires_a_project(time_page: TimePage) -> None:
    time_page.open_submenu_item("Reports", "Project Reports")
    time_page.view_project_report()

    assert "Required" in time_page.get_validation_errors()


@pytest.mark.time
@pytest.mark.regression
def test_customer_form_requires_a_name(time_page: TimePage) -> None:
    time_page.open_add_customer_form()
    time_page.save_form()

    assert time_page.get_validation_errors().count("Required") == 1


@pytest.mark.time
@pytest.mark.regression
def test_project_form_requires_name_and_customer(time_page: TimePage) -> None:
    time_page.open_add_project_form()
    time_page.save_form()

    assert time_page.get_validation_errors().count("Required") == 2
