from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class DirectoryPage(BasePage):
    directory_heading = (By.XPATH, "//h5[normalize-space()='Directory']")
    directory_cards = (By.CSS_SELECTOR, ".orangehrm-directory-card")
    employee_name_input = (
        By.XPATH,
        "//label[normalize-space()='Employee Name']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//input",
    )
    search_button = (
        By.XPATH,
        "//form//button[@type='submit' and normalize-space()='Search']",
    )
    reset_button = (
        By.XPATH,
        "//form//button[@type='reset' and normalize-space()='Reset']",
    )
    no_records_message = (
        By.XPATH,
        "//*[normalize-space()='No Records Found']",
    )

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.directory_heading)

    def set_employee_name_filter(self, employee_name: str) -> None:
        self.enter_text(self.employee_name_input, employee_name)

    def select_filter_option(self, label: str, option: str) -> None:
        self.click(self._dropdown_locator(label))
        self.click(self._option_locator(option))

    def get_employee_name_filter(self) -> str:
        return (
            self.wait_until_visible(self.employee_name_input).get_attribute("value")
            or ""
        )

    def get_filter_value(self, label: str) -> str:
        return self.get_text(self._dropdown_text_locator(label))

    def get_filter_options(self, label: str) -> list[str]:
        dropdown = self._dropdown_locator(label)
        self.click(dropdown)
        options = self.wait_for_elements((By.CSS_SELECTOR, "[role='option']"), 1)
        option_texts = [
            " ".join(option.text.split())
            for option in options
            if option.is_displayed()
        ]
        self.click(dropdown)
        return option_texts

    def search_directory(self) -> int:
        self.click(self.search_button)
        self.wait.until(
            lambda driver: any(
                card.is_displayed()
                for card in driver.find_elements(*self.directory_cards)
            )
            or any(
                message.is_displayed()
                for message in driver.find_elements(*self.no_records_message)
            )
        )
        return sum(
            card.is_displayed()
            for card in self.driver.find_elements(*self.directory_cards)
        )

    def reset_filters(self) -> None:
        self.click(self.reset_button)

    def is_no_records_message_displayed(self) -> bool:
        return any(
            message.is_displayed()
            for message in self.driver.find_elements(*self.no_records_message)
        )

    @staticmethod
    def _dropdown_locator(label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            f"//label[normalize-space()='{label}']"
            "/ancestor::div[contains(@class, 'oxd-input-group')]"
            "//div[contains(@class, 'oxd-select-text')]",
        )

    @staticmethod
    def _dropdown_text_locator(label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            f"//label[normalize-space()='{label}']"
            "/ancestor::div[contains(@class, 'oxd-input-group')]"
            "//div[contains(@class, 'oxd-select-text-input')]",
        )

    @staticmethod
    def _option_locator(option: str) -> tuple[str, str]:
        return (
            By.XPATH,
            f"//*[@role='option' and normalize-space()='{option}']",
        )
