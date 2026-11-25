from collections.abc import Iterator

import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config.config import BASE_URL, TIMEOUT
from pages.login_page import LoginPage
from pages.my_info_page import MyInfoPage
from pages.pim_page import (
    AddEmployeePage,
    EmployeeDetailsPage,
    PimConfigurationPage,
    PimDataImportPage,
    PimLookupPage,
    PimPage,
    PimReportFormPage,
    PimReportsPage,
)
from test_data.login_data import VALID_PASSWORD, VALID_USERNAME
from test_data.pim_data import (
    PIM_CONFIGURATION_ITEMS,
    PIM_LOOKUP_PAGES,
    create_employee_data,
    create_pim_lookup_name,
    create_pim_report_name,
)


def open_pim_page(driver: WebDriver) -> PimPage:
    LoginPage(driver).login(VALID_USERNAME, VALID_PASSWORD)
    WebDriverWait(driver, TIMEOUT).until(
        expected_conditions.url_contains("/dashboard/index")
    )
    driver.get(f"{BASE_URL}/web/index.php/pim/viewEmployeeList")

    page = PimPage(driver)
    page.wait_until_loaded()
    return page


def open_add_employee_page(driver: WebDriver) -> AddEmployeePage:
    pim_page = open_pim_page(driver)
    pim_page.open_add_employee()

    page = AddEmployeePage(driver)
    page.wait_until_loaded()
    return page


def open_employee_details_page(
    pim_page: PimPage,
    employee_id: str,
) -> EmployeeDetailsPage:
    pim_page.open_employee_list()
    assert pim_page.search_by_employee_id(employee_id)
    pim_page.open_employee_for_edit(employee_id)

    return EmployeeDetailsPage(pim_page.driver)


def open_employee_contact_details(
    pim_page: PimPage,
    employee_id: str,
) -> MyInfoPage:
    open_employee_details_page(pim_page, employee_id)
    contact_page = MyInfoPage(pim_page.driver)
    contact_page.open_contact_details()
    return contact_page


@pytest.fixture
def employee_record(driver: WebDriver) -> Iterator[tuple[PimPage, dict[str, str]]]:
    pim_page = open_pim_page(driver)
    employee = create_employee_data()
    pim_page.open_add_employee()

    add_employee_page = AddEmployeePage(driver)
    add_employee_page.wait_until_loaded()
    add_employee_page.add_employee(
        employee["first_name"],
        employee["middle_name"],
        employee["last_name"],
        employee["employee_id"],
    )
    yield pim_page, employee

    driver.get(f"{BASE_URL}/web/index.php/pim/viewEmployeeList")
    pim_page.wait_until_loaded()
    if pim_page.search_by_employee_id(employee["employee_id"]):
        pim_page.delete_employee(employee["employee_id"])


@pytest.fixture
def pim_lookup_record(
    driver: WebDriver,
    request: pytest.FixtureRequest,
) -> Iterator[tuple[PimLookupPage, str, list[str]]]:
    page_name, _ = request.param
    pim_page = open_pim_page(driver)
    pim_page.open_configuration_item(page_name)
    lookup_page = PimLookupPage(driver, page_name)
    lookup_page.wait_until_loaded()
    name = create_pim_lookup_name(page_name)
    cleanup_names = [name]

    try:
        lookup_page.open_add_form()
        lookup_page.set_name(name)
        lookup_page.save_form(name)
        yield lookup_page, name, cleanup_names
    finally:
        driver.get(f"{BASE_URL}/web/index.php/pim/viewEmployeeList")
        list_page = PimPage(driver)
        list_page.wait_until_loaded()
        list_page.open_configuration_item(page_name)
        lookup_page = PimLookupPage(driver, page_name)
        lookup_page.wait_until_loaded()
        for cleanup_name in cleanup_names:
            if lookup_page.has_record(cleanup_name):
                lookup_page.delete_record(cleanup_name)


@pytest.fixture
def pim_report_record(
    driver: WebDriver,
) -> Iterator[tuple[PimReportsPage, str, list[str]]]:
    pim_page = open_pim_page(driver)
    reports_page = pim_page.open_reports()
    report_name = create_pim_report_name()
    cleanup_names = [report_name]

    try:
        form_page = reports_page.open_add_report()
        form_page.set_report_name(report_name)
        form_page.add_display_field("Personal", "Employee Id")
        form_page.save_form(report_name)
        yield PimReportsPage(driver), report_name, cleanup_names
    finally:
        driver.get(f"{BASE_URL}/web/index.php/pim/viewEmployeeList")
        list_page = PimPage(driver)
        list_page.wait_until_loaded()
        reports_page = list_page.open_reports()
        for cleanup_name in cleanup_names:
            if reports_page.has_report(cleanup_name):
                reports_page.delete_report(cleanup_name)


@pytest.mark.pim
@pytest.mark.smoke
def test_employee_list_is_displayed(driver: WebDriver) -> None:
    pim_page = open_pim_page(driver)

    assert pim_page.get_heading() == "Employee Information"
    assert pim_page.is_add_employee_button_visible()


@pytest.mark.pim
@pytest.mark.smoke
def test_TC_PIM_001_add_employee_with_valid_information(
    employee_record: tuple[PimPage, dict[str, str]],
) -> None:
    pim_page, employee = employee_record
    details_page = EmployeeDetailsPage(pim_page.driver)

    assert details_page.get_first_name() == employee["first_name"]
    assert details_page.get_middle_name() == employee["middle_name"]
    assert details_page.get_last_name() == employee["last_name"]


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_002_first_name_is_mandatory(driver: WebDriver) -> None:
    add_page = open_add_employee_page(driver)
    add_page.set_last_name("TestEmployee")
    add_page.save()

    assert "Required" in add_page.get_validation_errors()


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_003_last_name_is_mandatory(driver: WebDriver) -> None:
    add_page = open_add_employee_page(driver)
    add_page.set_first_name("TestEmployee")
    add_page.save()

    assert "Required" in add_page.get_validation_errors()


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_004_invalid_employee_information_is_rejected(
    driver: WebDriver,
) -> None:
    add_page = open_add_employee_page(driver)
    add_page.save()

    assert add_page.get_validation_errors().count("Required") == 2


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_005_duplicate_employee_id_is_rejected(
    employee_record: tuple[PimPage, dict[str, str]],
    driver: WebDriver,
) -> None:
    _, employee = employee_record
    driver.get(f"{BASE_URL}/web/index.php/pim/addEmployee")
    add_page = AddEmployeePage(driver)
    add_page.wait_until_loaded()
    add_page.set_first_name("Duplicate")
    add_page.set_last_name("Employee")
    add_page.set_employee_id(employee["employee_id"])
    add_page.save()

    errors = add_page.get_validation_errors()
    assert any("already exists" in error.lower() for error in errors)


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_006_employee_is_displayed_after_saving(
    employee_record: tuple[PimPage, dict[str, str]],
) -> None:
    pim_page, employee = employee_record
    pim_page.open_employee_list()

    assert pim_page.search_by_employee_id(employee["employee_id"])
    row_text = pim_page.get_employee_row_text(employee["employee_id"])
    assert employee["first_name"] in row_text
    assert employee["last_name"] in row_text


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_007_search_by_employee_name(
    employee_record: tuple[PimPage, dict[str, str]],
) -> None:
    pim_page, employee = employee_record
    pim_page.open_employee_list()

    assert pim_page.search_by_employee_name(employee["first_name"])
    row_text = pim_page.get_employee_row_text(employee["employee_id"])
    assert employee["first_name"] in row_text
    assert employee["last_name"] in row_text


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_008_search_by_employee_id(
    employee_record: tuple[PimPage, dict[str, str]],
) -> None:
    pim_page, employee = employee_record
    pim_page.open_employee_list()

    assert pim_page.search_by_employee_id(employee["employee_id"])
    assert employee["first_name"] in pim_page.get_employee_row_text(
        employee["employee_id"]
    )


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_009_search_with_invalid_employee_name_returns_no_results(
    driver: WebDriver,
) -> None:
    pim_page = open_pim_page(driver)

    assert not pim_page.search_by_employee_name("NoSuchEmployee999")


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_010_reset_search_filters(
    employee_record: tuple[PimPage, dict[str, str]],
) -> None:
    pim_page, employee = employee_record
    pim_page.open_employee_list()
    assert pim_page.search_by_employee_id(employee["employee_id"])

    pim_page.reset_filters()

    assert pim_page.get_employee_id_filter() == ""
    assert pim_page.get_employee_name_filter() == ""


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_011_edit_employee_personal_details(
    employee_record: tuple[PimPage, dict[str, str]],
) -> None:
    pim_page, employee = employee_record
    pim_page.open_employee_list()
    assert pim_page.search_by_employee_id(employee["employee_id"])
    pim_page.open_employee_for_edit(employee["employee_id"])

    updated_first_name = f"{employee['first_name']}Edit"
    details_page = EmployeeDetailsPage(pim_page.driver)
    details_page.update_first_name(updated_first_name)

    assert details_page.get_first_name() == updated_first_name


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_012_edit_contact_information(
    employee_record: tuple[PimPage, dict[str, str]],
) -> None:
    pim_page, employee = employee_record
    contact_page = open_employee_contact_details(
        pim_page,
        employee["employee_id"],
    )
    updated_city = f"TestCity{employee['employee_id']}"
    contact_page.set_text_field("City", updated_city)

    assert contact_page.get_text_field_value("City") == updated_city


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_013_save_updated_employee_information(
    employee_record: tuple[PimPage, dict[str, str]],
) -> None:
    pim_page, employee = employee_record
    contact_page = open_employee_contact_details(
        pim_page,
        employee["employee_id"],
    )
    updated_email = f"employee{employee['employee_id']}@example.com"
    contact_page.set_text_field("Other Email", updated_email)
    contact_page.save_contact_details()

    assert contact_page.get_updated_message() == "Successfully Updated"


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_014_updated_employee_information_persists_after_reload(
    employee_record: tuple[PimPage, dict[str, str]],
) -> None:
    pim_page, employee = employee_record
    details_page = open_employee_details_page(
        pim_page,
        employee["employee_id"],
    )
    updated_first_name = f"{employee['first_name']}Persist"
    details_page.update_first_name(updated_first_name)
    pim_page.driver.refresh()
    details_page.wait.until(
        expected_conditions.text_to_be_present_in_element_value(
            EmployeeDetailsPage.first_name_input,
            updated_first_name,
        )
    )

    assert details_page.get_first_name() == updated_first_name


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_015_delete_employee(
    employee_record: tuple[PimPage, dict[str, str]],
) -> None:
    pim_page, employee = employee_record
    pim_page.open_employee_list()
    assert pim_page.search_by_employee_id(employee["employee_id"])

    pim_page.delete_employee(employee["employee_id"])

    assert not pim_page.has_employee(employee["employee_id"])


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_016_cancel_employee_deletion(
    employee_record: tuple[PimPage, dict[str, str]],
) -> None:
    pim_page, employee = employee_record
    pim_page.open_employee_list()
    assert pim_page.search_by_employee_id(employee["employee_id"])

    pim_page.cancel_delete_employee(employee["employee_id"])

    assert pim_page.has_employee(employee["employee_id"])


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_017_verify_employee_is_removed_after_delete_fallback(
    employee_record: tuple[PimPage, dict[str, str]],
) -> None:
    pim_page, employee = employee_record
    pim_page.open_employee_list()
    assert pim_page.search_by_employee_id(employee["employee_id"])
    pim_page.delete_employee(employee["employee_id"])

    assert not pim_page.has_employee(employee["employee_id"])


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_018_configuration_pages_navigation(
    driver: WebDriver,
) -> None:
    pim_page = open_pim_page(driver)

    for item in PIM_CONFIGURATION_ITEMS:
        configuration_page = pim_page.open_configuration_item(item)

        assert configuration_page.get_page_name() == item


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_019_employee_list_dropdown_options_and_reset(
    driver: WebDriver,
) -> None:
    pim_page = open_pim_page(driver)

    include_options = pim_page.get_filter_dropdown_options("Include")
    assert include_options == [
        "Current Employees Only",
        "Current and Past Employees",
        "Past Employees Only",
    ]
    assert pim_page.get_filter_dropdown_options("Employment Status")
    assert pim_page.get_filter_dropdown_options("Job Title")
    assert pim_page.get_filter_dropdown_options("Sub Unit")

    pim_page.select_filter_dropdown_option(
        "Include",
        "Current and Past Employees",
    )
    assert (
        pim_page.get_filter_dropdown_value("Include")
        == "Current and Past Employees"
    )

    pim_page.reset_filters()

    assert pim_page.get_filter_dropdown_value("Include") == "Current Employees Only"
    assert pim_page.get_employee_id_filter() == ""
    assert pim_page.get_employee_name_filter() == ""


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_020_add_employee_login_details_validation(
    driver: WebDriver,
) -> None:
    add_page = open_add_employee_page(driver)
    add_page.enable_login_details()

    assert set(add_page.get_login_status_options()) == {"Enabled", "Disabled"}

    add_page.set_first_name("Login")
    add_page.set_last_name("Validation")
    add_page.save()

    validation_errors = add_page.get_validation_errors()
    assert validation_errors.count("Required") == 2
    assert "Passwords do not match" in validation_errors


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_021_data_import_requires_a_file(
    driver: WebDriver,
) -> None:
    pim_page = open_pim_page(driver)
    pim_page.open_configuration_item("Data Import")
    import_page = PimDataImportPage(driver)
    import_page.wait_until_loaded()

    assert import_page.upload_without_file() == ["Required"]


@pytest.mark.pim
@pytest.mark.regression
@pytest.mark.parametrize(
    "page_name",
    PIM_LOOKUP_PAGES,
    ids=[page[0].lower().replace(" ", "-") for page in PIM_LOOKUP_PAGES],
)
def test_TC_PIM_022_configuration_lookup_forms_require_a_name(
    driver: WebDriver,
    page_name: tuple[str, str],
) -> None:
    configuration_item, heading = page_name
    pim_page = open_pim_page(driver)
    pim_page.open_configuration_item(configuration_item)
    lookup_page = PimLookupPage(driver, heading)
    lookup_page.wait_until_loaded()
    lookup_page.open_add_form()

    assert lookup_page.save_empty_form() == ["Required"]

    lookup_page.cancel_form()


@pytest.mark.pim
@pytest.mark.regression
@pytest.mark.parametrize(
    "pim_lookup_record",
    PIM_LOOKUP_PAGES,
    indirect=True,
    ids=[page[0].lower().replace(" ", "-") for page in PIM_LOOKUP_PAGES],
)
def test_TC_PIM_023_configuration_lookup_record_can_be_edited_and_deleted(
    pim_lookup_record: tuple[PimLookupPage, str, list[str]],
) -> None:
    page, original_name, cleanup_names = pim_lookup_record
    page.open_edit_form(original_name)
    updated_name = f"{original_name} Updated"
    cleanup_names.append(updated_name)
    page.set_name(updated_name)
    page.save_form(updated_name)

    assert page.has_record(updated_name)

    page.delete_record(updated_name)

    assert not page.has_record(updated_name)


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_024_report_form_validation_and_dropdowns(
    driver: WebDriver,
) -> None:
    pim_page = open_pim_page(driver)
    reports_page = pim_page.open_reports()
    form_page = reports_page.open_add_report()

    assert form_page.save_empty_form() == ["Required"]
    assert {"Employee Name", "Job Title"}.issubset(
        set(form_page.get_dropdown_options("Selection Criteria"))
    )
    assert form_page.get_dropdown_options("Include") == [
        "Current Employees Only",
        "Current and Past Employees",
        "Past Employees Only",
    ]
    assert "Personal" in form_page.get_dropdown_options(
        "Select Display Field Group"
    )

    form_page.select_dropdown_option("Select Display Field Group", "Personal")
    assert "Employee Id" in form_page.get_dropdown_options(
        "Select Display Field"
    )
    form_page.select_dropdown_option("Select Display Field", "Employee Id")
    form_page.select_dropdown_option(
        "Include",
        "Current and Past Employees",
    )
    form_page.cancel_form()


@pytest.mark.pim
@pytest.mark.regression
def test_TC_PIM_025_report_can_be_searched_reset_run_edited_and_deleted(
    pim_report_record: tuple[PimReportsPage, str, list[str]],
) -> None:
    reports_page, original_name, cleanup_names = pim_report_record

    assert reports_page.search_by_report_name(original_name)
    assert reports_page.get_report_name_filter() == original_name

    reports_page.reset_filters()

    assert reports_page.get_report_name_filter() == ""
    assert reports_page.run_report(original_name) == original_name

    reports_page = PimPage(reports_page.driver).open_reports()
    edit_page = reports_page.open_edit_report(original_name)
    updated_name = f"{original_name} Updated"
    cleanup_names.append(updated_name)
    edit_page.set_report_name(updated_name)
    edit_page.save_form(updated_name)

    reports_page = PimReportsPage(reports_page.driver)
    assert reports_page.has_report(updated_name)
    reports_page.delete_report(updated_name)

    assert not reports_page.has_report(updated_name)
