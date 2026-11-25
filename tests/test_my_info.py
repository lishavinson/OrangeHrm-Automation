import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config.config import BASE_URL, TIMEOUT
from pages.login_page import LoginPage
from pages.my_info_page import MyInfoPage
from test_data.login_data import VALID_PASSWORD, VALID_USERNAME


@pytest.fixture
def my_info_page(driver: WebDriver) -> MyInfoPage:
    LoginPage(driver).login(VALID_USERNAME, VALID_PASSWORD)
    WebDriverWait(driver, TIMEOUT).until(
        expected_conditions.url_contains("/dashboard/index")
    )
    driver.get(f"{BASE_URL}/web/index.php/pim/viewMyDetails")

    page = MyInfoPage(driver)
    page.wait_until_loaded()
    return page


@pytest.mark.my_info
@pytest.mark.smoke
def test_personal_details_page_is_displayed(
    my_info_page: MyInfoPage,
) -> None:
    assert my_info_page.get_heading() == "Personal Details"
    assert isinstance(my_info_page.get_text_field_value("First Name"), str)
    assert isinstance(my_info_page.get_text_field_value("Last Name"), str)
    assert isinstance(my_info_page.get_text_field_value("Other Id"), str)


@pytest.mark.my_info
@pytest.mark.smoke
def test_contact_details_page_is_displayed(
    my_info_page: MyInfoPage,
) -> None:
    my_info_page.open_contact_details()

    assert my_info_page.get_heading() == "Contact Details"
    assert isinstance(my_info_page.get_text_field_value("Street 1"), str)
    assert isinstance(my_info_page.get_text_field_value("City"), str)
    assert isinstance(my_info_page.get_text_field_value("Mobile"), str)
    assert isinstance(my_info_page.get_text_field_value("Work Email"), str)


@pytest.mark.my_info
@pytest.mark.regression
def test_personal_and_contact_details_tabs_can_be_switched(
    my_info_page: MyInfoPage,
) -> None:
    my_info_page.open_contact_details()
    assert my_info_page.get_heading() == "Contact Details"

    my_info_page.open_personal_details()
    assert my_info_page.get_heading() == "Personal Details"
