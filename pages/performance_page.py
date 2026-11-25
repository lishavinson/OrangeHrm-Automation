from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions

from config.config import BASE_URL
from pages.base_page import BasePage


class PerformancePage(BasePage):
    performance_heading = (By.XPATH, "//h6[normalize-space()='Performance']")
    employee_reviews_heading = (
        By.XPATH,
        "//h5[normalize-space()='Employee Reviews']",
    )
    kpi_list_heading = (
        By.XPATH,
        "//h5[normalize-space()='Key Performance Indicators for Job Title']",
    )
    kpi_add_button = (
        By.XPATH,
        "//button[contains(normalize-space(.), 'Add')]",
    )
    kpi_save_button = (By.XPATH, "//button[normalize-space()='Save']")
    kpi_cancel_button = (By.XPATH, "//button[normalize-space()='Cancel']")
    validation_errors = (
        By.CSS_SELECTOR,
        "span.oxd-input-field-error-message",
    )
    dropdown_options = (By.CSS_SELECTOR, "[role='option']")
    kpi_rows = (By.CSS_SELECTOR, "[role='row']")
    kpi_filter_toggle = (
        By.XPATH,
        "//h5[normalize-space()='Key Performance Indicators for Job Title']"
        "/ancestor::div[contains(@class, 'oxd-table-filter-header')]//button",
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
    pagination_buttons = (
        By.CSS_SELECTOR,
        "nav[aria-label='Pagination Navigation'] button",
    )
    selected_page_button = (
        By.CSS_SELECTOR,
        "nav[aria-label='Pagination Navigation'] "
        "button.oxd-pagination-page-item--page-selected",
    )
    delete_confirmation = (By.CSS_SELECTOR, "div[role='document']")
    confirm_delete_button = (
        By.XPATH,
        "//button[normalize-space()='Yes, Delete']",
    )
    cancel_delete_button = (
        By.XPATH,
        "//button[normalize-space()='No, Cancel']",
    )
    submenu_categories = {
        "Configure": (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']//li"
            "[.//*[normalize-space()='Configure']]",
        ),
        "Manage Reviews": (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']//li"
            "[.//*[normalize-space()='Manage Reviews']]",
        ),
    }
    submenu_items = {
        ("Configure", "KPIs"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='KPIs']",
        ),
        ("Configure", "Trackers"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Trackers']",
        ),
        ("Manage Reviews", "Manage Reviews"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Manage Reviews']",
        ),
        ("Manage Reviews", "My Reviews"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='My Reviews']",
        ),
        ("Manage Reviews", "Employee Reviews"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Employee Reviews']",
        ),
    }
    direct_submenu_items = {
        ("Trackers", "My Trackers"): (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']//a[normalize-space()='My Trackers']",
        ),
        ("Trackers", "Employee Trackers"): (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']"
            "//a[normalize-space()='Employee Trackers']",
        ),
    }
    submenu_routes = {
        ("Configure", "KPIs"): "/performance/searchKpi",
        ("Configure", "Trackers"): "/performance/viewPerformanceTracker",
        ("Manage Reviews", "Manage Reviews"): (
            "/performance/searchPerformanceReview"
        ),
        ("Manage Reviews", "My Reviews"): "/performance/myPerformanceReview",
        ("Manage Reviews", "Employee Reviews"): (
            "/performance/searchEvaluatePerformanceReview"
        ),
        ("Trackers", "My Trackers"): (
            "/performance/viewMyPerformanceTrackerList"
        ),
        ("Trackers", "Employee Trackers"): (
            "/performance/viewEmployeePerformanceTrackerList"
        ),
    }

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def open_performance_module(self) -> None:
        self.driver.get(f"{BASE_URL}/web/index.php/performance/viewPerformanceModule")
        self.wait_until_loaded()

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.performance_heading)
        self.wait_until_visible(self.employee_reviews_heading)

    def open_submenu_item(self, category: str, item: str) -> None:
        key = (category, item)
        if key in self.submenu_items:
            self.click(self.submenu_categories[category])
            self.click(self.submenu_items[key])
        else:
            self.click(self.direct_submenu_items[key])

        self.wait.until(
            expected_conditions.url_contains(self.submenu_routes[key])
        )
        self.wait_until_visible(self._heading_locator(self.page_heading_for(key)))

    def is_heading_visible(self, heading: str) -> bool:
        return self.is_visible(self._heading_locator(heading))

    def open_kpi_add_form(self) -> None:
        self.click(self.kpi_add_button)
        self.wait.until(expected_conditions.url_contains("/performance/saveKpi"))
        self.wait_until_visible(self._kpi_form_heading())

    def select_first_available_job_title(self) -> str | None:
        self.click(self._dropdown_locator("Job Title"))
        _, job_titles = self.wait.until(self._read_job_title_options)
        if not job_titles:
            return None
        self.click(self._option_locator(job_titles[0]))
        return job_titles[0]

    def select_job_title(self, job_title: str) -> None:
        self.click(self._dropdown_locator("Job Title"))
        self.click(self._option_locator(job_title))

    def get_selected_job_title(self) -> str:
        return self.get_text(self._dropdown_text_locator("Job Title"))

    def set_kpi_field(self, label: str, value: str) -> None:
        self.enter_text(self._field_input_locator(label), value)

    def get_kpi_field_value(self, label: str) -> str:
        return (
            self.wait_until_visible(self._field_input_locator(label)).get_attribute(
                "value"
            )
            or ""
        )

    def get_validation_errors(self) -> list[str]:
        self.wait.until(
            lambda driver: any(
                error.is_displayed()
                for error in driver.find_elements(*self.validation_errors)
            )
        )
        return [
            error.text.strip()
            for error in self.driver.find_elements(*self.validation_errors)
            if error.is_displayed()
        ]

    def save_kpi_form(self) -> None:
        self.click(self.kpi_save_button)
        self.wait.until(
            expected_conditions.url_contains("/performance/searchKpi")
        )
        self.wait_until_kpi_list_loaded()

    def submit_invalid_kpi_form(self) -> None:
        self.click(self.kpi_save_button)

    def cancel_kpi_form(self) -> None:
        self.click(self.kpi_cancel_button)
        self.wait.until(
            expected_conditions.url_contains("/performance/searchKpi")
        )
        self.wait_until_kpi_list_loaded()

    def wait_until_kpi_list_loaded(self) -> None:
        self.wait_until_visible(self.kpi_list_heading)
        self.wait.until(
            lambda driver: self._kpi_list_has_loaded()
        )

    def get_kpi_rows(self) -> list[WebElement]:
        return [
            row
            for row in self.driver.find_elements(*self.kpi_rows)
            if row.is_displayed()
            and row.find_elements(By.CSS_SELECTOR, "[role='cell']")
        ]

    def get_first_kpi_job_title(self) -> str | None:
        rows = self.get_kpi_rows()
        if not rows:
            return None
        return self._get_kpi_row_values(rows[0]).get("Job Title")

    def search_kpis_by_job_title(self, job_title: str) -> None:
        if not any(
            element.is_displayed()
            for element in self.driver.find_elements(
                *self._dropdown_locator("Job Title")
            )
        ):
            self.click(self.kpi_filter_toggle)
        self.select_job_title(job_title)
        self.click(self.search_button)
        self.wait.until(
            lambda driver: self._kpi_search_results_loaded(job_title)
        )

    def reset_kpi_search(self) -> None:
        self.click(self.reset_button)
        self.wait.until(
            expected_conditions.text_to_be_present_in_element(
                self._dropdown_text_locator("Job Title"),
                "-- Select --",
            )
        )

    def has_kpi_record(self, name: str) -> bool:
        self.wait_until_kpi_list_loaded()
        if self._find_kpi_row_on_current_page(name):
            return True

        page_numbers = [
            button.text.strip()
            for button in self.driver.find_elements(*self.pagination_buttons)
            if button.text.strip().isdigit()
        ]
        for page_number in page_numbers:
            if page_number == self._get_selected_page_number():
                continue
            self.click(
                (
                    By.XPATH,
                    "//nav[@aria-label='Pagination Navigation']//button"
                    f"[normalize-space()='{page_number}']",
                )
            )
            self.wait.until(
                expected_conditions.text_to_be_present_in_element(
                    self.selected_page_button,
                    page_number,
                )
            )
            self.wait_until_kpi_list_loaded()
            if self._find_kpi_row_on_current_page(name):
                return True
        return False

    def open_edit_kpi_form(self, name: str) -> None:
        row = self._find_kpi_row(name)
        row.find_element(
            By.XPATH,
            ".//button[.//i[contains(@class, 'bi-pencil-fill')]]",
        ).click()
        self.wait.until(expected_conditions.url_contains("/performance/saveKpi/"))
        self.wait_until_visible(self._kpi_form_heading())
        self.wait.until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".oxd-form-loader")
            )
        )
        self.wait.until(
            lambda driver: self.get_kpi_field_value(
                "Key Performance Indicator"
            )
            == name
        )

    def delete_kpi_record(self, name: str) -> None:
        row = self._find_kpi_row(name)
        row.find_element(
            By.XPATH,
            ".//button[.//i[contains(@class, 'bi-trash')]]",
        ).click()
        self.wait.until(
            expected_conditions.visibility_of_element_located(
                self.delete_confirmation
            )
        )
        self.click(self.confirm_delete_button)
        self.wait.until(
            lambda driver: self._find_kpi_row_on_current_page(name) is None
        )

    def _find_kpi_row(self, name: str) -> WebElement:
        if self.has_kpi_record(name):
            row = self._find_kpi_row_on_current_page(name)
            if row is not None:
                return row
        raise LookupError(f"KPI {name!r} was not found in the visible list.")

    def _find_kpi_row_on_current_page(self, name: str) -> WebElement | None:
        try:
            for row in self.get_kpi_rows():
                if (
                    self._get_kpi_row_values(row).get(
                        "Key Performance Indicator"
                    )
                    == name
                ):
                    return row
        except StaleElementReferenceException:
            return None
        return None

    def _kpi_search_results_loaded(self, job_title: str) -> bool:
        try:
            if self._is_no_records_message_visible():
                return True
            rows = self.get_kpi_rows()
            return bool(rows) and all(
                self._get_kpi_row_values(row).get("Job Title") == job_title
                for row in rows
            )
        except StaleElementReferenceException:
            return False

    def _get_selected_page_number(self) -> str:
        try:
            buttons = self.driver.find_elements(*self.selected_page_button)
            return buttons[0].text.strip() if buttons else ""
        except StaleElementReferenceException:
            return ""

    def _get_kpi_row_values(self, row: WebElement) -> dict[str, str]:
        headers = self.driver.find_elements(
            By.CSS_SELECTOR,
            "[role='columnheader']",
        )
        cells = row.find_elements(By.CSS_SELECTOR, "[role='cell']")
        return {
            header.text.strip(): cell.text.strip()
            for header, cell in zip(headers, cells)
            if header.text.strip()
        }

    def _kpi_list_has_loaded(self) -> bool:
        try:
            return bool(self.get_kpi_rows()) or self._is_no_records_message_visible()
        except StaleElementReferenceException:
            return False

    def _read_job_title_options(
        self,
        driver: WebDriver,
    ) -> tuple[bool, list[str]] | bool:
        try:
            options = driver.find_elements(*self.dropdown_options)
            if not options:
                return False
            return True, [
                title
                for option in options
                if (title := option.text.strip())
                and title not in {"-- Select --", "No Records Found"}
            ]
        except StaleElementReferenceException:
            return False

    def _is_no_records_message_visible(self) -> bool:
        return any(
            message.is_displayed()
            for message in self.driver.find_elements(*self.no_records_message)
        )

    @staticmethod
    def _heading_locator(heading: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//*[self::p or self::h5 or self::h6]"
            f"[normalize-space()='{heading}']",
        )

    @staticmethod
    def _kpi_form_heading() -> tuple[str, str]:
        return (
            By.XPATH,
            "//*[self::p or self::h5 or self::h6]"
            "[normalize-space()='Add Key Performance Indicator' "
            "or normalize-space()='Edit Key Performance Indicator']",
        )

    @staticmethod
    def _field_input_locator(label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//form[contains(@class, 'oxd-form')]"
            "//div[contains(@class, 'oxd-input-group')]"
            f"[.//label[normalize-space()='{label}']]//input",
        )

    @staticmethod
    def _dropdown_locator(label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//div[contains(@class, 'oxd-input-group')]"
            f"[.//label[normalize-space()='{label}']]"
            "//div[contains(@class, 'oxd-select-text')]",
        )

    @staticmethod
    def _dropdown_text_locator(label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//div[contains(@class, 'oxd-input-group')]"
            f"[.//label[normalize-space()='{label}']]"
            "//div[contains(@class, 'oxd-select-text-input')]",
        )

    @staticmethod
    def _option_locator(option: str) -> tuple[str, str]:
        return (
            By.XPATH,
            f"//*[@role='option' and normalize-space()='{option}']",
        )

    @staticmethod
    def page_heading_for(key: tuple[str, str]) -> str:
        return {
            ("Configure", "KPIs"): "Key Performance Indicators for Job Title",
            ("Configure", "Trackers"): "Performance Trackers",
            ("Manage Reviews", "Manage Reviews"): "Manage Performance Reviews",
            ("Manage Reviews", "My Reviews"): "My Reviews",
            ("Manage Reviews", "Employee Reviews"): "Employee Reviews",
            ("Trackers", "My Trackers"): "My Performance Trackers",
            ("Trackers", "Employee Trackers"): (
                "Employee Performance Trackers"
            ),
        }[key]
