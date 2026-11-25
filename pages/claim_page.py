from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class ClaimPage(BasePage):
    employee_claims_heading = (
        By.XPATH,
        "//h5[normalize-space()='Employee Claims']",
    )
    submit_claim_heading = (
        By.XPATH,
        "//h6[normalize-space()='Create Claim Request']",
    )
    validation_errors = (
        By.CSS_SELECTOR,
        "span.oxd-input-field-error-message",
    )
    employee_name_input = (
        By.XPATH,
        "//label[normalize-space()='Employee Name']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//input",
    )
    reference_id_input = (
        By.XPATH,
        "//label[normalize-space()='Reference Id']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//input",
    )
    search_button = (
        By.XPATH,
        "//form//button[@type='submit' and normalize-space()='Search']",
    )
    reset_button = (
        By.XPATH,
        "//form//button[@type='button' and normalize-space()='Reset']",
    )
    remarks_input = (
        By.XPATH,
        "//label[normalize-space()='Remarks']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//textarea",
    )
    create_claim_button = (
        By.XPATH,
        "//form//button[@type='submit' and normalize-space()='Create']",
    )
    cancel_claim_button = (
        By.XPATH,
        "//form//button[@type='button' and normalize-space()='Cancel']",
    )

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.employee_claims_heading)

    def set_employee_name_filter(self, employee_name: str) -> None:
        self.enter_text(self.employee_name_input, employee_name)

    def set_reference_id_filter(self, reference_id: str) -> None:
        self.enter_text(self.reference_id_input, reference_id)

    def select_filter_option(self, label: str, option: str) -> None:
        self.click(self._dropdown_locator(label))
        self.click(self._option_locator(option))

    def set_date_filter(self, label: str, value: str) -> None:
        self.enter_text(self._input_locator(label), value)

    def get_filter_value(self, label: str) -> str:
        return self.get_text(self._dropdown_text_locator(label))

    def search_claims(self) -> None:
        self.click(self.search_button)

    def reset_claim_filters(self) -> None:
        self.click(self.reset_button)

    def open_submit_claim(self) -> None:
        self.click(
            (
                By.XPATH,
                "//nav[@aria-label='Topbar Menu']//a"
                "[normalize-space()='Submit Claim']",
            )
        )
        self.wait_until_visible(self.submit_claim_heading)

    def select_request_option(self, label: str, option: str) -> None:
        self.click(self._dropdown_locator(label))
        self.click(self._option_locator(option))

    def set_remarks(self, remarks: str) -> None:
        self.enter_text(self.remarks_input, remarks)

    def create_claim_request(self) -> None:
        self.click(self.create_claim_button)

    def cancel_claim_request(self) -> None:
        self.click(self.cancel_claim_button)

    def get_validation_errors(self) -> list[str]:
        self.wait.until(
            lambda driver: any(
                error.is_displayed()
                for error in driver.find_elements(*self.validation_errors)
            )
        )
        return [
            error.text
            for error in self.driver.find_elements(*self.validation_errors)
            if error.is_displayed()
        ]

    @staticmethod
    def _input_locator(label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            f"//label[normalize-space()='{label}']"
            "/ancestor::div[contains(@class, 'oxd-input-group')]//input",
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
