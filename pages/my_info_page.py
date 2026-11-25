from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions

from pages.base_page import BasePage


class MyInfoPage(BasePage):
    personal_details_tab = (
        By.XPATH,
        "//a[normalize-space()='Personal Details']",
    )
    contact_details_tab = (
        By.XPATH,
        "//a[normalize-space()='Contact Details']",
    )
    personal_details_heading = (
        By.XPATH,
        "//h6[normalize-space()='Personal Details']",
    )
    contact_details_heading = (
        By.XPATH,
        "//h6[normalize-space()='Contact Details']",
    )
    updated_message = (
        By.XPATH,
        "//*[normalize-space()='Successfully Updated']",
    )
    logged_in_user_name = (By.CSS_SELECTOR, ".oxd-userdropdown-name")
    personal_details_save_button = (
        By.XPATH,
        "//form[.//input[@name='firstName']]"
        "//button[normalize-space()='Save']",
    )
    contact_details_save_button = (
        By.XPATH,
        "//form[.//label[normalize-space()='Street 1']]"
        "//button[normalize-space()='Save']",
    )
    name_field_locators = {
        "First Name": (By.NAME, "firstName"),
        "Middle Name": (By.NAME, "middleName"),
        "Last Name": (By.NAME, "lastName"),
    }

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def wait_until_loaded(self) -> None:
        self.wait.until(
            lambda driver: any(
                element.is_displayed()
                for locator in (
                    self.personal_details_heading,
                    self.contact_details_heading,
                )
                for element in driver.find_elements(*locator)
            )
        )

    def open_personal_details(self) -> None:
        self.click(self.personal_details_tab)
        self.wait.until(
            expected_conditions.visibility_of_element_located(
                self.personal_details_heading
            )
        )

    def open_contact_details(self) -> None:
        self.click(self.contact_details_tab)
        self.wait.until(
            expected_conditions.visibility_of_element_located(
                self.contact_details_heading
            )
        )

    def get_heading(self) -> str:
        heading = self.wait.until(
            lambda driver: next(
                (
                    element
                    for locator in (
                        self.personal_details_heading,
                        self.contact_details_heading,
                    )
                    for element in driver.find_elements(*locator)
                    if element.is_displayed()
                ),
                False,
            )
        )
        return heading.text

    def get_logged_in_user_name(self) -> str:
        return self.get_text(self.logged_in_user_name)

    def _field_locator(self, label: str) -> tuple[str, str]:
        if label in self.name_field_locators:
            return self.name_field_locators[label]

        return (
            By.XPATH,
            f'//label[normalize-space()="{label}"]'
            "/ancestor::div[contains(concat(' ', normalize-space(@class), ' '), "
            "' oxd-input-group ')]//input",
        )

    def set_text_field(self, label: str, value: str) -> None:
        self.enter_text(self._field_locator(label), value)

    def get_text_field_value(self, label: str) -> str:
        return (
            self.wait_until_visible(self._field_locator(label))
            .get_attribute("value")
            or ""
        )

    def _dropdown_locator(self, label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            f'//label[normalize-space()="{label}"]'
            "/ancestor::div[contains(concat(' ', normalize-space(@class), ' '), "
            "' oxd-input-group ')]"
            "//div[contains(concat(' ', normalize-space(@class), ' '), "
            "' oxd-select-text-input ')]",
        )

    def select_dropdown_option(self, label: str, option: str) -> None:
        self.click(self._dropdown_locator(label))
        option_locator = (
            By.XPATH,
            f'//div[@role="option" and normalize-space()="{option}"]',
        )
        self.click(option_locator)

    def get_selected_dropdown_option(self, label: str) -> str:
        selected_option = (
            By.XPATH,
            f'//label[normalize-space()="{label}"]'
            "/ancestor::div[contains(concat(' ', normalize-space(@class), ' '), "
            "' oxd-input-group ')]"
            "//div[contains(concat(' ', normalize-space(@class), ' '), "
            "' oxd-select-text-input ')]",
        )
        return self.get_text(selected_option)

    def select_gender(self, gender: str) -> None:
        self.click(
            (
                By.XPATH,
                f'//label[normalize-space()="{gender}"]',
            )
        )

    def save_personal_details(self) -> None:
        self.click(self.personal_details_save_button)
        self.wait_until_visible(self.updated_message)

    def save_contact_details(self) -> None:
        self.click(self.contact_details_save_button)
        self.wait_until_visible(self.updated_message)

    def get_updated_message(self) -> str:
        return self.get_text(self.updated_message)
