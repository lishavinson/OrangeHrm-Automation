from collections.abc import Iterator

import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config.config import BASE_URL, TIMEOUT
from pages.admin_page import (
    AdminPage,
    AdminSubcategoryFormPage,
    CorporateBrandingPage,
    GeneralInformationPage,
    OrganizationStructurePage,
)
from pages.login_page import LoginPage
from test_data.admin_data import (
    ADMIN_ROLE,
    ADMIN_REQUIRED_FORM_PAGES,
    ADMIN_SUBCATEGORIES,
    CORPORATE_BRANDING_FIELDS,
    ENABLED_STATUS,
    GENERAL_INFORMATION_FIELDS,
    NO_MATCH_USERNAME,
    ROLE_OPTIONS,
    STATUS_OPTIONS,
    create_admin_subcategory_data,
)
from test_data.login_data import VALID_PASSWORD, VALID_USERNAME


@pytest.fixture
def admin_page(driver: WebDriver) -> AdminPage:
    LoginPage(driver).login(VALID_USERNAME, VALID_PASSWORD)
    WebDriverWait(driver, TIMEOUT).until(
        expected_conditions.url_contains("/dashboard/index")
    )
    driver.get(f"{BASE_URL}/web/index.php/admin/viewSystemUsers")

    page = AdminPage(driver)
    page.wait_until_loaded()
    return page


def _record_name(record: dict[str, str]) -> str:
    return record.get("Name") or next(iter(record.values()))


@pytest.fixture
def admin_subcategory_record(
    admin_page: AdminPage,
    request: pytest.FixtureRequest,
) -> Iterator[
    tuple[
        AdminSubcategoryFormPage,
        dict[str, str],
        list[str],
    ]
]:
    category, item, heading = request.param
    subcategory_page = AdminSubcategoryFormPage(admin_page.driver, heading)
    record = create_admin_subcategory_data(item)
    cleanup_names: list[str] = []

    try:
        admin_page.open_subcategory(category, item, heading)
        subcategory_page.wait_until_loaded()
        subcategory_page.open_add_form()
        assert set(record).issubset(
            set(subcategory_page.get_form_field_labels())
        )
        subcategory_page.set_fields(record)
        created_name = _record_name(record)
        cleanup_names.append(created_name)
        subcategory_page.save_form(created_name)
        assert subcategory_page.has_record(created_name)
        yield subcategory_page, record, cleanup_names
    finally:
        if cleanup_names:
            admin_page.open_subcategory(category, item, heading)
            subcategory_page.wait_until_loaded()
            for name in cleanup_names:
                if subcategory_page.has_record(name):
                    subcategory_page.delete_record(name)


@pytest.mark.admin
@pytest.mark.smoke
def test_TC_ADMIN_001_system_users_page_and_filters(
    admin_page: AdminPage,
) -> None:
    assert admin_page.get_heading() == "System Users"
    assert all(
        admin_page.is_filter_control_visible(label)
        for label in ("Username", "User Role", "Employee Name", "Status")
    )
    assert admin_page.get_usernames()
    assert admin_page.get_user_action_count(VALID_USERNAME) == 2


@pytest.mark.admin
@pytest.mark.regression
def test_TC_ADMIN_002_user_filters_search_and_reset(
    admin_page: AdminPage,
) -> None:
    original_summary = admin_page.get_records_summary()
    employee_name = admin_page.get_user_field(
        VALID_USERNAME,
        "Employee Name",
    )

    assert admin_page.get_dropdown_options("User Role") == ROLE_OPTIONS
    assert admin_page.get_dropdown_options("Status") == STATUS_OPTIONS

    admin_page.set_username_filter(VALID_USERNAME)
    admin_page.select_user_role(ADMIN_ROLE)
    admin_page.select_status(ENABLED_STATUS)
    admin_page.search(expected_result_count=1)
    assert admin_page.get_usernames() == [VALID_USERNAME]

    admin_page.reset_filters(expected_summary=original_summary)
    admin_page.set_employee_name_filter(employee_name)
    admin_page.search(expected_result_count=1)
    assert admin_page.get_usernames() == [VALID_USERNAME]

    admin_page.reset_filters(expected_summary=original_summary)
    admin_page.set_username_filter(NO_MATCH_USERNAME)
    admin_page.search_for_no_results()
    assert not admin_page.get_user_rows()

    admin_page.reset_filters(expected_summary=original_summary)
    assert admin_page.get_filter_values() == {
        "Username": "",
        "Employee Name": "",
        "User Role": "-- Select --",
        "Status": "-- Select --",
    }


@pytest.mark.admin
@pytest.mark.regression
def test_TC_ADMIN_003_add_user_required_field_validation(
    admin_page: AdminPage,
) -> None:
    add_user_page = admin_page.open_add_user()
    add_user_page.save()
    validation_messages = add_user_page.get_validation_messages()

    assert validation_messages.count("Required") == 4
    assert "Passwords do not match" not in validation_messages

    add_user_page.cancel()
    assert add_user_page.is_back_on_system_users()


@pytest.mark.admin
@pytest.mark.regression
def test_TC_ADMIN_004_admin_subcategory_navigation(
    admin_page: AdminPage,
) -> None:
    for category, item, heading in ADMIN_SUBCATEGORIES:
        admin_page.open_subcategory(category, item, heading)


@pytest.mark.admin
@pytest.mark.regression
def test_TC_ADMIN_005_general_information_fields_and_edit_mode(
    admin_page: AdminPage,
) -> None:
    admin_page.open_subcategory(
        "Organization",
        "General Information",
        "General Information",
    )
    page = GeneralInformationPage(admin_page.driver)

    assert set(page.get_field_labels()) == set(GENERAL_INFORMATION_FIELDS)

    page.enable_edit_mode()
    assert page.is_save_button_visible()


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize(
    ("category", "item", "heading", "required_count"),
    ADMIN_REQUIRED_FORM_PAGES,
    ids=[page[1].lower().replace(" ", "-") for page in ADMIN_REQUIRED_FORM_PAGES],
)
def test_TC_ADMIN_006_subcategory_add_form_requires_fields(
    admin_page: AdminPage,
    category: str,
    item: str,
    heading: str,
    required_count: int,
) -> None:
    admin_page.open_subcategory(category, item, heading)
    page = AdminSubcategoryFormPage(admin_page.driver, heading)
    page.wait_until_loaded()
    page.open_add_form()

    assert page.save_empty_form().count("Required") == required_count

    page.cancel_form()


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize(
    "admin_subcategory_record",
    [page[:3] for page in ADMIN_REQUIRED_FORM_PAGES],
    indirect=True,
    ids=[page[1].lower().replace(" ", "-") for page in ADMIN_REQUIRED_FORM_PAGES],
)
def test_TC_ADMIN_009_subcategory_details_can_be_edited_and_deleted(
    admin_subcategory_record: tuple[
        AdminSubcategoryFormPage,
        dict[str, str],
        list[str],
    ],
) -> None:
    page, record, cleanup_names = admin_subcategory_record
    identifier_key = "Name" if "Name" in record else next(iter(record))
    original_name = record[identifier_key]

    page.open_edit_form(original_name)
    assert {
        field: page.get_field_value(field)
        for field in record
    } == record

    updated_record = dict(record)
    updated_name = f"{original_name} Updated"
    updated_record[identifier_key] = updated_name
    cleanup_names.append(updated_name)
    if "Description" in updated_record:
        updated_record["Description"] = f"{record['Description']} updated"
    if "City" in updated_record:
        updated_record["City"] = f"{record['City']} Updated"
    page.set_fields(updated_record)
    page.save_form(updated_name)

    assert page.has_record(updated_name)
    page.open_edit_form(updated_name)
    assert {
        field: page.get_field_value(field)
        for field in updated_record
    } == updated_record
    page.cancel_form()
    page.delete_record(updated_name)

    assert not page.has_record(updated_name)


@pytest.mark.admin
@pytest.mark.regression
def test_TC_ADMIN_007_structure_page_has_no_editable_hierarchy_in_demo(
    admin_page: AdminPage,
) -> None:
    admin_page.open_subcategory(
        "Organization",
        "Structure",
        "Organization Structure",
    )
    page = OrganizationStructurePage(admin_page.driver)
    page.wait_until_loaded()

    assert not page.get_visible_hierarchy_controls()


@pytest.mark.admin
@pytest.mark.regression
def test_TC_ADMIN_008_corporate_branding_preview(
    admin_page: AdminPage,
) -> None:
    admin_page.open_subcategory(
        "More",
        "Corporate Branding",
        "Corporate Branding",
    )
    page = CorporateBrandingPage(admin_page.driver)

    assert set(page.get_field_labels()) == set(CORPORATE_BRANDING_FIELDS)

    page.preview()
    assert "/admin/addTheme" in admin_page.driver.current_url
