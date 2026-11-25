from datetime import date, datetime, timedelta

import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config.config import BASE_URL, TIMEOUT
from pages.leave_page import LeavePage
from pages.login_page import LoginPage
from pages.my_info_page import MyInfoPage
from test_data.leave_data import (
    LEAVE_TEST_BALANCE,
    LEAVE_TEST_EMPLOYEE_NAME,
    LEAVE_TEST_PASSWORD,
    LEAVE_TEST_TYPE,
    LEAVE_TEST_USERNAME,
    create_excess_leave_dates,
    create_leave_comment,
    create_valid_leave_dates,
)


@pytest.fixture(scope="module", autouse=True)
def validate_leave_test_settings() -> None:
    if LEAVE_TEST_BALANCE <= 0:
        pytest.fail(
            "LEAVE_TEST_BALANCE must be greater than zero.",
            pytrace=False,
        )


def open_leave_list(driver: WebDriver) -> LeavePage:
    LoginPage(driver).login(LEAVE_TEST_USERNAME, LEAVE_TEST_PASSWORD)
    WebDriverWait(driver, TIMEOUT).until(
        expected_conditions.url_contains("/dashboard/index")
    )
    page = LeavePage(driver)
    page.open_leave_list()
    return page


def open_apply_leave_page(driver: WebDriver) -> LeavePage:
    leave_page = open_leave_list(driver)
    employee_name = LEAVE_TEST_EMPLOYEE_NAME
    if not employee_name:
        driver.get(f"{BASE_URL}/web/index.php/pim/viewMyDetails")
        my_info_page = MyInfoPage(driver)
        my_info_page.wait_until_loaded()
        name_parts = (
            my_info_page.get_text_field_value("First Name"),
            my_info_page.get_text_field_value("Middle Name"),
            my_info_page.get_text_field_value("Last Name"),
        )
        employee_name = " ".join(part for part in name_parts if part)
        if not employee_name:
            employee_name = my_info_page.get_logged_in_user_name()
    leave_page.ensure_leave_entitlement(
        employee_name,
        LEAVE_TEST_TYPE,
        LEAVE_TEST_BALANCE,
    )
    leave_page.open_apply_leave()
    return leave_page


def prepare_valid_application(leave_page: LeavePage) -> str:
    unavailable_dates = get_existing_leave_dates(leave_page)
    from_date, to_date = create_valid_leave_dates(unavailable_dates)
    comment = create_leave_comment()
    leave_page.open_apply_leave()
    leave_page.select_leave_type(LEAVE_TEST_TYPE)
    leave_page.set_leave_dates(from_date, to_date)
    leave_page.set_leave_comments(comment)
    return comment


def get_existing_leave_dates(leave_page: LeavePage) -> set[date]:
    leave_page.open_my_leave_list()
    dates: set[date] = set()
    for row in leave_page.get_my_leave_rows():
        if not row.splitlines():
            continue
        date_parts = row.splitlines()[0].strip().split(" to ")
        if len(date_parts) > 2:
            raise ValueError(f"Unexpected leave date range in row: {row!r}")
        start_date = datetime.strptime(date_parts[0], "%Y-%d-%m").date()
        end_date = (
            datetime.strptime(date_parts[1], "%Y-%d-%m").date()
            if len(date_parts) == 2
            else start_date
        )
        current_date = start_date
        while current_date <= end_date:
            dates.add(current_date)
            current_date += timedelta(days=1)
    leave_page.open_apply_leave()
    return dates


@pytest.mark.leave
@pytest.mark.smoke
def test_leave_list_is_displayed(driver: WebDriver) -> None:
    leave_page = open_leave_list(driver)

    assert leave_page.get_leave_list_heading() == "Leave List"


@pytest.mark.leave
@pytest.mark.regression
def test_leave_list_search_displays_results_or_empty_state(
    driver: WebDriver,
) -> None:
    leave_page = open_leave_list(driver)
    statuses = leave_page.search_leave_list()

    assert statuses or leave_page.is_no_records_message_displayed()


@pytest.mark.leave
@pytest.mark.regression
def test_leave_list_filters_can_be_reset(driver: WebDriver) -> None:
    leave_page = open_leave_list(driver)
    leave_page.select_leave_status("Rejected")
    assert "Rejected" in leave_page.get_selected_leave_statuses()

    leave_page.reset_filters()

    assert leave_page.get_selected_leave_statuses() == []


@pytest.mark.leave
@pytest.mark.regression
def test_leave_list_search_filters_by_status(driver: WebDriver) -> None:
    leave_page = open_leave_list(driver)
    leave_page.select_leave_status("Pending Approval")

    statuses = leave_page.search_leave_list()

    assert all(status == "Pending Approval" for status in statuses)
    if not statuses:
        assert leave_page.is_visible(leave_page.no_records_message)


@pytest.mark.leave
@pytest.mark.regression
@pytest.mark.parametrize(
    ("menu", "item", "route_fragment"),
    [
        pytest.param("topbar", "Apply", "/leave/applyLeave", id="apply-leave"),
        pytest.param(
            "topbar", "My Leave", "/leave/viewMyLeaveList", id="my-leave"
        ),
        pytest.param(
            "Entitlements",
            "Add Entitlements",
            "/leave/addLeaveEntitlement",
            id="add-entitlements",
        ),
        pytest.param(
            "Entitlements",
            "Employee Entitlements",
            "/leave/viewLeaveEntitlements",
            id="employee-entitlements",
        ),
        pytest.param(
            "Reports",
            "Leave Entitlements and Usage Report",
            "/leave/viewLeaveBalanceReport",
            id="leave-report",
        ),
        pytest.param(
            "Configure", "Leave Types", "/leave/leaveTypeList", id="configure"
        ),
        pytest.param(
            "More", "Leave List", "/leave/viewLeaveList", id="leave-list"
        ),
        pytest.param(
            "More", "Assign Leave", "/leave/assignLeave", id="assign-leave"
        ),
    ],
)
def test_leave_subcategory_navigation(
    driver: WebDriver,
    menu: str,
    item: str,
    route_fragment: str,
) -> None:
    leave_page = open_leave_list(driver)
    if menu == "topbar":
        leave_page.open_leave_topbar_item(item)
    else:
        leave_page.open_leave_submenu_item(menu, item)

    assert route_fragment in driver.current_url


@pytest.mark.leave
@pytest.mark.smoke
def test_apply_leave_page_displays_leave_balance(driver: WebDriver) -> None:
    leave_page = open_apply_leave_page(driver)

    balance = leave_page.get_leave_balance()
    amount, unit = balance.split(maxsplit=1)
    assert float(amount) >= 0
    assert unit == "Day(s)"


@pytest.mark.leave
@pytest.mark.regression
def test_my_leave_list_displays_records_or_empty_state(
    driver: WebDriver,
) -> None:
    leave_page = open_leave_list(driver)
    leave_page.open_my_leave_list()
    rows = leave_page.get_my_leave_rows()

    assert rows or leave_page.is_no_records_message_displayed()


@pytest.mark.leave
@pytest.mark.smoke
def test_TC_LEAVE_001_apply_valid_leave(driver: WebDriver) -> None:
    leave_page = open_apply_leave_page(driver)
    comment = prepare_valid_application(leave_page)
    leave_page.submit_leave_application()

    assert leave_page.get_application_success_message() == "Successfully Saved"
    leave_page.open_my_leave_list()
    assert leave_page.wait_for_my_leave_application(comment)


@pytest.mark.leave
@pytest.mark.regression
def test_TC_LEAVE_002_leave_type_is_required(driver: WebDriver) -> None:
    leave_page = open_apply_leave_page(driver)
    from_date, to_date = create_valid_leave_dates()
    leave_page.set_leave_dates(from_date, to_date)
    leave_page.submit_leave_application()

    assert "Required" in leave_page.get_application_validation_errors()


@pytest.mark.leave
@pytest.mark.regression
def test_TC_LEAVE_003_dates_are_required(driver: WebDriver) -> None:
    leave_page = open_apply_leave_page(driver)
    leave_page.select_leave_type(LEAVE_TEST_TYPE)
    leave_page.submit_leave_application()

    assert leave_page.get_application_validation_errors().count("Required") == 2


@pytest.mark.leave
@pytest.mark.regression
def test_TC_LEAVE_004_invalid_dates_are_rejected(driver: WebDriver) -> None:
    leave_page = open_apply_leave_page(driver)
    leave_page.select_leave_type(LEAVE_TEST_TYPE)
    leave_page.set_leave_dates("invalid", "invalid")
    leave_page.submit_leave_application()

    assert any(
        "valid date" in error.lower()
        for error in leave_page.get_application_validation_errors()
    )


@pytest.mark.leave
@pytest.mark.regression
def test_TC_LEAVE_005_exceeding_leave_balance_is_rejected(
    driver: WebDriver,
) -> None:
    leave_page = open_apply_leave_page(driver)
    unavailable_dates = get_existing_leave_dates(leave_page)
    try:
        from_date, to_date = create_excess_leave_dates(unavailable_dates)
    except ValueError as error:
        pytest.skip(str(error))
    leave_page.select_leave_type(LEAVE_TEST_TYPE)
    leave_page.set_leave_dates(from_date, to_date)
    leave_page.submit_leave_application()

    error_message = leave_page.wait_for_application_result()
    assert any(
        message in error_message
        for message in ("Leave Balance Exceeded", "Failed to Submit")
    ), f"Expected an over-balance rejection, got {error_message!r}"


@pytest.mark.leave
@pytest.mark.regression
def test_assign_leave_requires_employee_type_and_dates(
    driver: WebDriver,
) -> None:
    leave_page = open_leave_list(driver)
    leave_page.open_assign_leave()
    leave_page.submit_assign_leave()

    assert leave_page.get_application_validation_errors().count("Required") == 4
