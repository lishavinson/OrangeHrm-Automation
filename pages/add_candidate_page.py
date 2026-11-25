from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class AddCandidatePage(BasePage):
    heading = (By.XPATH, "//h6[normalize-space()='Add Candidate']")
    first_name_input = (By.NAME, "firstName")
    middle_name_input = (By.NAME, "middleName")
    last_name_input = (By.NAME, "lastName")
    email_input = (
        By.XPATH,
        "//label[normalize-space()='Email']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//input",
    )
    contact_number_input = (
        By.XPATH,
        "//label[normalize-space()='Contact Number']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//input",
    )
    vacancy_dropdown = (
        By.XPATH,
        "//label[normalize-space()='Vacancy']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]"
        "//div[contains(@class, 'oxd-select-text')]",
    )
    dropdown_options = (By.CSS_SELECTOR, "[role='option']")
    resume_input = (
        By.XPATH,
        "//label[normalize-space()='Resume']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//input[@type='file']",
    )
    keywords_input = (
        By.CSS_SELECTOR,
        "input[placeholder='Enter comma seperated words...']",
    )
    application_date_input = (
        By.CSS_SELECTOR,
        "input[placeholder='yyyy-dd-mm']",
    )
    notes_input = (
        By.XPATH,
        "//label[normalize-space()='Notes']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//textarea",
    )
    consent_checkbox = (
        By.XPATH,
        "//label[normalize-space()='Consent to keep data']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//input[@type='checkbox']",
    )
    consent_label = (
        By.XPATH,
        "//label[normalize-space()='Consent to keep data']",
    )
    cancel_button = (By.XPATH, "//button[normalize-space()='Cancel']")
    save_button = (By.XPATH, "//button[normalize-space()='Save']")
    validation_errors = (By.CSS_SELECTOR, ".oxd-input-field-error-message")
    success_message = (
        By.XPATH,
        "//*[normalize-space()='Successfully Saved']",
    )

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.heading)

    def get_heading(self) -> str:
        return self.get_text(self.heading)

    def set_first_name(self, first_name: str) -> None:
        self.enter_text(self.first_name_input, first_name)

    def set_middle_name(self, middle_name: str) -> None:
        self.enter_text(self.middle_name_input, middle_name)

    def set_last_name(self, last_name: str) -> None:
        self.enter_text(self.last_name_input, last_name)

    def set_email(self, email: str) -> None:
        self.enter_text(self.email_input, email)

    def set_contact_number(self, contact_number: str) -> None:
        self.enter_text(self.contact_number_input, contact_number)

    def select_vacancy(self, vacancy: str) -> str | None:
        def open_dropdown(driver: WebDriver) -> bool:
            try:
                dropdown = driver.find_element(*self.vacancy_dropdown)
                if dropdown.is_displayed() and dropdown.is_enabled():
                    dropdown.click()
                    return True
            except StaleElementReferenceException:
                return False
            return False

        self.wait.until(open_dropdown)

        def get_visible_options(driver: WebDriver) -> list[str] | bool:
            try:
                options = [
                    option.text.strip()
                    for option in driver.find_elements(*self.dropdown_options)
                    if option.is_displayed()
                ]
                return options or False
            except StaleElementReferenceException:
                return False

        options = self.wait.until(get_visible_options)
        available_vacancies = [
            option
            for option in options
            if option not in {"-- Select --", "No Records Found"}
        ]
        if not available_vacancies:
            return None
        selected_vacancy = (
            vacancy if vacancy in available_vacancies else available_vacancies[0]
        )

        self.click(
            (
                By.XPATH,
                "//*[@role='option' and normalize-space()="
                f"'{selected_vacancy}']",
            )
        )
        return selected_vacancy

    def upload_resume(self, file_path: str) -> None:
        self.wait_until_visible(self.resume_input).send_keys(file_path)

    def set_keywords(self, keywords: str) -> None:
        self.enter_text(self.keywords_input, keywords)

    def set_application_date(self, application_date: str) -> None:
        self.enter_text(self.application_date_input, application_date)

    def set_notes(self, notes: str) -> None:
        self.enter_text(self.notes_input, notes)

    def set_consent_to_keep_data(self, consent: bool) -> None:
        checkbox = self.wait.until(
            lambda driver: driver.find_element(*self.consent_checkbox)
        )
        if checkbox.is_selected() != consent:
            self.click(self.consent_label)

    def get_consent_to_keep_data(self) -> bool:
        return self.wait_until_visible(self.consent_checkbox).is_selected()

    def cancel(self) -> None:
        self.click(self.cancel_button)

    def save(self) -> None:
        self.click(self.save_button)

    def wait_until_saved(self) -> str:
        return self.get_text(self.success_message)

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
