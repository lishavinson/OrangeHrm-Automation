from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions

from pages.base_page import BasePage


class RecruitmentPage(BasePage):
    candidates_heading = (
        By.CSS_SELECTOR,
        ".oxd-table-filter-header h5",
    )
    add_candidate_button = (
        By.XPATH,
        "//button[normalize-space()='Add']",
    )
    toast_container = (By.CSS_SELECTOR, ".oxd-toast-container")
    filter_toggle = (
        By.CSS_SELECTOR,
        ".oxd-table-filter-header-options button",
    )
    candidate_name_input = (
        By.CSS_SELECTOR,
        "input[placeholder='Type for hints...']",
    )
    keywords_input = (
        By.CSS_SELECTOR,
        "input[placeholder='Enter comma seperated words...']",
    )
    application_date_from_input = (By.CSS_SELECTOR, "input[placeholder='From']")
    application_date_to_input = (By.CSS_SELECTOR, "input[placeholder='To']")
    search_button = (
        By.CSS_SELECTOR,
        ".oxd-table-filter-area button[type='submit']",
    )
    reset_button = (
        By.CSS_SELECTOR,
        ".oxd-table-filter-area button[type='reset']",
    )
    dropdown_options = (By.CSS_SELECTOR, "[role='option']")
    candidate_suggestions = (By.CSS_SELECTOR, "[role='option']")
    candidate_rows = (By.CSS_SELECTOR, ".oxd-table-body [role='row']")
    no_records_message = (
        By.XPATH,
        "//*[normalize-space()='No Records Found']",
    )
    delete_confirmation = (
        By.XPATH,
        "//div[@role='document']"
        "[.//*[contains(normalize-space(), 'delete')]]",
    )
    confirm_delete_button = (
        By.XPATH,
        "//button[normalize-space()='Yes, Delete']",
    )
    candidate_name_error = (
        By.XPATH,
        "//input[@placeholder='Type for hints...']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]"
        "//*[contains(@class, 'oxd-input-field-error-message')]",
    )

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.candidates_heading)
        self.wait.until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, ".oxd-table")
            )
        )

    def get_heading(self) -> str:
        return self.get_text(self.candidates_heading)

    def is_add_candidate_button_visible(self) -> bool:
        return self.is_visible(self.add_candidate_button)

    def open_add_candidate(self) -> None:
        self.wait.until(
            expected_conditions.invisibility_of_element_located(
                self.toast_container
            )
        )
        self.click(self.add_candidate_button)
        self.wait.until(expected_conditions.url_contains("/recruitment/addCandidate"))

    def _ensure_filters_visible(self) -> None:
        visible_name_inputs = [
            element
            for element in self.driver.find_elements(*self.candidate_name_input)
            if element.is_displayed()
        ]
        if not visible_name_inputs:
            self.click(self.filter_toggle)
        self.wait_until_visible(self.candidate_name_input)

    @staticmethod
    def _filter_dropdown(label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            f"//label[normalize-space()='{label}']"
            "/ancestor::div[contains(@class, 'oxd-input-group')]"
            "//div[contains(@class, 'oxd-select-text')]",
        )

    def select_filter(self, label: str, option_text: str) -> None:
        self._ensure_filters_visible()
        dropdown_locator = self._filter_dropdown(label)

        def open_dropdown(driver: WebDriver) -> bool:
            try:
                dropdown = driver.find_element(*dropdown_locator)
                if dropdown.is_displayed() and dropdown.is_enabled():
                    dropdown.click()
                    return True
            except StaleElementReferenceException:
                return False
            return False

        self.wait.until(open_dropdown)

        def choose_option(driver: WebDriver) -> bool:
            try:
                for option in driver.find_elements(*self.dropdown_options):
                    if option.is_displayed() and option.text.strip() == option_text:
                        option.click()
                        return True
            except StaleElementReferenceException:
                return False
            return False

        self.wait.until(choose_option)

    def set_candidate_name(self, candidate_name: str) -> None:
        self._ensure_filters_visible()
        self.enter_text(self.candidate_name_input, candidate_name)

    def select_candidate_suggestion(self, candidate_name: str) -> None:
        expected_name = " ".join(candidate_name.split())

        def choose_suggestion(driver: WebDriver) -> bool:
            try:
                for option in driver.find_elements(*self.candidate_suggestions):
                    if (
                        option.is_displayed()
                        and " ".join(option.text.split()) == expected_name
                    ):
                        option.click()
                        return True
            except StaleElementReferenceException:
                return False
            return False

        self.wait.until(choose_suggestion)

    def set_keywords(self, keywords: str) -> None:
        self._ensure_filters_visible()
        self.enter_text(self.keywords_input, keywords)

    def set_application_date_range(self, start_date: str, end_date: str) -> None:
        self._ensure_filters_visible()
        self.enter_text(self.application_date_from_input, start_date)
        self.enter_text(self.application_date_to_input, end_date)

    def search_candidates(self) -> None:
        self.click(self.search_button)

        def results_loaded(driver: WebDriver) -> bool:
            try:
                rows = driver.find_elements(*self.candidate_rows)
                for row in rows:
                    try:
                        if row.is_displayed():
                            return True
                    except StaleElementReferenceException:
                        continue
                return any(
                    message.is_displayed()
                    for message in driver.find_elements(*self.no_records_message)
                )
            except StaleElementReferenceException:
                return False

        self.wait.until(results_loaded)

    def search_candidate_by_name(self, candidate_name: str) -> list[str]:
        search_text = candidate_name.split(maxsplit=1)[0]
        self.set_candidate_name(search_text)
        self.select_candidate_suggestion(candidate_name)
        self.search_candidates()
        return self.get_candidate_rows()

    def open_candidate_profile(self, candidate_name: str) -> None:
        row = self._candidate_row(candidate_name)
        view_button = row.find_element(
            By.XPATH,
            ".//button[.//i[contains(@class, 'bi-eye-fill')]]",
        )
        view_button.click()
        self.wait.until(
            expected_conditions.url_contains("/recruitment/addCandidate/")
        )

    def _candidate_row(self, candidate_name: str) -> WebElement:
        expected_name = " ".join(candidate_name.split())

        def candidate_row_available(driver: WebDriver) -> WebElement | bool:
            try:
                for row in driver.find_elements(*self.candidate_rows):
                    try:
                        if row.is_displayed() and expected_name in " ".join(
                            row.text.split()
                        ):
                            return row
                    except StaleElementReferenceException:
                        continue
                return False
            except StaleElementReferenceException:
                return False

        return self.wait.until(candidate_row_available)

    def delete_candidate(self, candidate_name: str) -> None:
        row = self._candidate_row(candidate_name)
        expected_name = " ".join(candidate_name.split())
        delete_button = row.find_element(
            By.XPATH,
            ".//button[.//i[contains(@class, 'bi-trash')]]",
        )
        delete_button.click()
        self.wait.until(
            expected_conditions.visibility_of_element_located(
                self.delete_confirmation
            )
        )
        self.click(self.confirm_delete_button)
        self.wait.until(
            lambda driver: not any(
                expected_name in " ".join(row.text.split())
                for row in driver.find_elements(*self.candidate_rows)
                if row.is_displayed()
            )
        )

    def reset_filters(self) -> None:
        self.click(self.reset_button)
        self.wait.until(
            lambda driver: driver.find_element(
                *self.keywords_input
            ).get_attribute("value")
            == ""
        )

    def get_keywords(self) -> str:
        return self.wait_until_visible(self.keywords_input).get_attribute("value")

    def get_candidate_rows(self) -> list[str]:
        rows: list[str] = []
        try:
            for row in self.driver.find_elements(*self.candidate_rows):
                try:
                    if row.is_displayed():
                        rows.append(row.text)
                except StaleElementReferenceException:
                    continue
        except StaleElementReferenceException:
            return rows
        return rows

    def has_candidate_name_validation_error(self) -> bool:
        return self.wait.until(
            lambda driver: any(
                error.is_displayed()
                for error in driver.find_elements(*self.candidate_name_error)
            )
        )

    def get_candidate_name_validation_error(self) -> str:
        self.has_candidate_name_validation_error()
        return self.get_text(self.candidate_name_error)
