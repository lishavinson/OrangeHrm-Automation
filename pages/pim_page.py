from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions

from pages.base_page import BasePage


class PimPage(BasePage):
    employee_information_heading = (
        By.CSS_SELECTOR,
        ".oxd-table-filter-header h5",
    )
    add_employee_button = (
        By.XPATH,
        "//button[normalize-space()='Add' or normalize-space()='添加']",
    )
    filter_toggle = (
        By.CSS_SELECTOR,
        ".oxd-table-filter-header-options button",
    )
    employee_id_input = (
        By.XPATH,
        "//label[normalize-space()='Employee Id' or "
        "normalize-space()='员工识别号']/parent::div/parent::div//input",
    )
    employee_name_input = (
        By.XPATH,
        "//label[normalize-space()='Employee Name']/parent::div/parent::div//input",
    )
    search_button = (
        By.CSS_SELECTOR,
        "form.oxd-form button[type='submit']",
    )
    reset_button = (
        By.XPATH,
        "//div[contains(@class, 'oxd-table-filter-area')]"
        "//button[normalize-space()='Reset']",
    )
    autocomplete_options = (By.CSS_SELECTOR, "[role='option']")
    no_records_message = (
        By.XPATH,
        "//*[normalize-space()='No Records Found']",
    )
    employee_list_link = (
        By.XPATH,
        "//nav[@aria-label='Topbar Menu']//a[normalize-space()='Employee List' "
        "or normalize-space()='员工列表']",
    )
    configuration_menu = (
        By.XPATH,
        "//nav[@aria-label='Topbar Menu']//span"
        "[normalize-space()='Configuration']",
    )
    reports_link = (
        By.XPATH,
        "//nav[@aria-label='Topbar Menu']//a[normalize-space()='Reports']",
    )

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.employee_information_heading)

    def get_heading(self) -> str:
        return self.get_text(self.employee_information_heading)

    def is_add_employee_button_visible(self) -> bool:
        return self.is_visible(self.add_employee_button)

    def open_add_employee(self) -> None:
        self.click(self.add_employee_button)
        self.wait.until(expected_conditions.url_contains("/pim/addEmployee"))

    def open_employee_list(self) -> None:
        self.click(self.employee_list_link)
        self.wait_until_loaded()

    def open_configuration_item(self, item: str) -> "PimConfigurationPage":
        self.click(self.configuration_menu)
        self.click(
            (
                By.XPATH,
                "//nav[@aria-label='Topbar Menu']"
                f"//*[@role='menuitem' and normalize-space()='{item}']",
            )
        )
        page = PimConfigurationPage(self.driver, item)
        page.wait_until_loaded()
        return page

    def open_reports(self) -> "PimReportsPage":
        self.click(self.reports_link)
        page = PimReportsPage(self.driver)
        page.wait_until_loaded()
        return page

    def _ensure_filters_visible(self) -> None:
        if not any(
            element.is_displayed()
            for element in self.driver.find_elements(*self.employee_id_input)
        ):
            self.click(self.filter_toggle)

    def get_filter_dropdown_options(self, label: str) -> list[str]:
        self._ensure_filters_visible()
        self.click(self._filter_dropdown_locator(label))
        options = self.wait_for_elements(
            (By.CSS_SELECTOR, "[role='option']"),
            minimum_count=1,
        )
        option_texts = [option.text.strip() for option in options]
        self.click(self._filter_dropdown_locator(label))
        return option_texts

    def get_filter_dropdown_value(self, label: str) -> str:
        self._ensure_filters_visible()
        return self.get_text(self._filter_dropdown_text_locator(label)).strip()

    def select_filter_dropdown_option(self, label: str, option: str) -> None:
        self._ensure_filters_visible()
        self.click(self._filter_dropdown_locator(label))
        self.click(
            (
                By.XPATH,
                f"//*[@role='option' and normalize-space()='{option}']",
            )
        )

    def _employee_row(self, employee_id: str) -> tuple[str, str]:
        return (
            By.XPATH,
            f"//div[@role='row'][contains(normalize-space(.), '{employee_id}')]",
        )

    def _click_current_element(self, locator: tuple[str, str]) -> None:
        def click_when_available(driver: WebDriver) -> bool:
            try:
                element = driver.find_element(*locator)
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    return True
            except StaleElementReferenceException:
                return False
            return False

        self.wait.until(click_when_available)

    def search_by_employee_id(self, employee_id: str) -> bool:
        try:
            self._ensure_filters_visible()
            self.enter_text(self.employee_id_input, employee_id)
            self.click(self.search_button)

            def results_loaded(driver: WebDriver) -> bool:
                try:
                    rows = driver.find_elements(*self._employee_row(employee_id))
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
            return self.has_employee(employee_id)
        except TimeoutException:
            return False

    def search_by_employee_name(self, employee_name: str) -> bool:
        try:
            self._ensure_filters_visible()
            self.enter_text(self.employee_name_input, employee_name)

            def select_employee_suggestion(driver: WebDriver) -> str | bool:
                for option in driver.find_elements(*self.autocomplete_options):
                    try:
                        if not option.is_displayed():
                            continue
                        if option.text.strip() == "No Records Found":
                            return "not found"
                        if employee_name in option.text:
                            option.click()
                            return "selected"
                    except StaleElementReferenceException:
                        continue
                return False

            suggestion_result = self.wait.until(select_employee_suggestion)
            self.click(self.search_button)

            if suggestion_result == "not found":
                self.wait.until(
                    expected_conditions.invisibility_of_element_located(
                        self.autocomplete_options
                    )
                )
                self.wait.until(
                    lambda driver: any(
                        message.is_displayed()
                        for message in driver.find_elements(*self.no_records_message)
                    )
                )
                return False

            def search_result_loaded(driver: WebDriver) -> str | bool:
                try:
                    if any(
                        row.is_displayed() and employee_name in row.text
                        for row in driver.find_elements(
                            By.CSS_SELECTOR,
                            ".oxd-table-body [role='row']",
                        )
                    ):
                        return "found"
                    if any(
                        message.is_displayed()
                        for message in driver.find_elements(*self.no_records_message)
                    ):
                        return "not found"
                    return False
                except StaleElementReferenceException:
                    return False

            return self.wait.until(search_result_loaded) == "found"
        except TimeoutException:
            return False

    def reset_filters(self) -> None:
        self.click(self.reset_button)

        def filters_are_reset(driver: WebDriver) -> bool:
            try:
                return not driver.find_element(
                    *self.employee_id_input
                ).get_attribute("value") and not driver.find_element(
                    *self.employee_name_input
                ).get_attribute("value")
            except StaleElementReferenceException:
                return False

        self.wait.until(filters_are_reset)

    def get_employee_id_filter(self) -> str:
        return (
            self.wait_until_visible(self.employee_id_input).get_attribute("value")
            or ""
        )

    def get_employee_name_filter(self) -> str:
        return (
            self.wait_until_visible(self.employee_name_input).get_attribute("value")
            or ""
        )

    def has_employee(self, employee_id: str) -> bool:
        try:
            return any(
                row.is_displayed()
                for row in self.driver.find_elements(*self._employee_row(employee_id))
            )
        except StaleElementReferenceException:
            return False

    def get_employee_row_text(self, employee_id: str) -> str:
        locator = self._employee_row(employee_id)

        def get_text_when_available(driver: WebDriver) -> str | bool:
            try:
                for row in driver.find_elements(*locator):
                    try:
                        if row.is_displayed():
                            return row.text
                    except StaleElementReferenceException:
                        continue
                return False
            except StaleElementReferenceException:
                return False

        text = self.wait.until(get_text_when_available)
        if not text:
            raise RuntimeError(f"Employee row for {employee_id!r} was not visible.")
        return str(text)

    def open_employee_for_edit(self, employee_id: str) -> None:
        edit_button = (
            By.XPATH,
            f"{self._employee_row(employee_id)[1]}"
            "//button[.//i[contains(@class, 'bi-pencil-fill')]]",
        )
        self._click_current_element(edit_button)
        self.wait.until(
            expected_conditions.url_contains("/pim/viewPersonalDetails/")
        )

    def delete_employee(self, employee_id: str) -> None:
        row = self.wait.until(
            lambda driver: next(
                (
                    row
                    for row in driver.find_elements(*self._employee_row(employee_id))
                    if row.is_displayed()
                ),
                False,
            )
        )
        delete_button = row.find_element(
            By.XPATH,
            ".//button[.//i[contains(@class, 'bi-trash')]]",
        )
        delete_button.click()
        confirmation_button = (
            By.XPATH,
            "//button[normalize-space()='Yes, Delete']",
        )
        self.wait.until(
            expected_conditions.visibility_of_element_located(confirmation_button)
        )
        self.click(confirmation_button)
        self.wait.until(
            lambda driver: not any(
                row.is_displayed()
                for row in driver.find_elements(*self._employee_row(employee_id))
            )
        )

    def cancel_delete_employee(self, employee_id: str) -> None:
        delete_button = (
            By.XPATH,
            f"{self._employee_row(employee_id)[1]}"
            "//button[.//i[contains(@class, 'bi-trash')]]",
        )
        self._click_current_element(delete_button)
        self.click((By.XPATH, "//button[normalize-space()='No, Cancel']"))
        self.wait.until(
            expected_conditions.invisibility_of_element_located(
                (By.XPATH, "//div[@role='document']")
            )
        )
        self.wait.until(
            expected_conditions.visibility_of_element_located(
                self._employee_row(employee_id)
            )
        )

    @staticmethod
    def _filter_dropdown_locator(label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//form[contains(@class, 'oxd-form')]"
            "//div[contains(@class, 'oxd-input-group')]"
            f"[.//label[normalize-space()='{label}']]"
            "//div[contains(@class, 'oxd-select-text')]",
        )

    @staticmethod
    def _filter_dropdown_text_locator(label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//form[contains(@class, 'oxd-form')]"
            "//div[contains(@class, 'oxd-input-group')]"
            f"[.//label[normalize-space()='{label}']]"
            "//div[contains(@class, 'oxd-select-text-input')]",
        )


class PimConfigurationPage(BasePage):
    optional_fields_checkboxes = (By.CSS_SELECTOR, "input[type='checkbox']")
    save_button = (By.XPATH, "//button[normalize-space()='Save']")

    def __init__(self, driver: WebDriver, page_name: str) -> None:
        super().__init__(driver)
        self.page_name = page_name
        self.page_heading = (
            By.XPATH,
            "//*[self::p or self::h6]"
            f"[normalize-space()='{page_name}']",
        )

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.page_heading)

    def get_page_name(self) -> str:
        return self.get_text(self.page_heading).strip()

    def get_visible_checkbox_count(self) -> int:
        return sum(
            checkbox.is_displayed()
            for checkbox in self.driver.find_elements(
                *self.optional_fields_checkboxes
            )
        )

    def is_save_button_visible(self) -> bool:
        return self.is_visible(self.save_button)


class PimDataImportPage(BasePage):
    heading = (By.XPATH, "//p[normalize-space()='Data Import']")
    upload_button = (By.XPATH, "//button[normalize-space()='Upload']")
    validation_errors = (
        By.CSS_SELECTOR,
        ".oxd-input-field-error-message",
    )

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.heading)

    def upload_without_file(self) -> list[str]:
        self.click(self.upload_button)
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


class PimLookupPage(BasePage):
    add_button = (By.XPATH, "//button[normalize-space()='Add']")
    save_button = (By.XPATH, "//button[normalize-space()='Save']")
    cancel_button = (By.XPATH, "//button[normalize-space()='Cancel']")
    validation_errors = (
        By.CSS_SELECTOR,
        ".oxd-input-field-error-message",
    )
    delete_confirmation_button = (
        By.XPATH,
        "//button[normalize-space()='Yes, Delete']",
    )

    def __init__(self, driver: WebDriver, page_name: str) -> None:
        super().__init__(driver)
        self.page_name = page_name
        self.page_heading = (
            By.XPATH,
            f"//p[normalize-space()='{page_name}']",
        )
        self.name_input = (
            By.XPATH,
            "//div[contains(@class, 'oxd-input-group')]"
            "[.//label[normalize-space()='Name']]//input",
        )

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.page_heading)

    def open_add_form(self) -> None:
        self.click(self.add_button)
        self.wait_until_visible(self.save_button)
        self.wait_until_visible(
            (
                By.XPATH,
                f"//p[normalize-space()='Add {self.page_name[:-1]}']",
            )
        )

    def set_name(self, name: str) -> None:
        self.enter_text(self.name_input, name)

    def save_form(self, expected_name: str | None = None) -> None:
        self.click(self.save_button)
        self.wait_until_visible(self.page_heading)
        if expected_name is not None:
            self.wait.until(lambda driver: self.has_record(expected_name))

    def save_empty_form(self) -> list[str]:
        self.click(self.save_button)
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

    def cancel_form(self) -> None:
        self.click(self.cancel_button)
        self.wait_until_visible(self.page_heading)

    def has_record(self, name: str) -> bool:
        return any(
            row.is_displayed()
            for row in self.driver.find_elements(
                *self._record_row_locator(name)
            )
        )

    def open_edit_form(self, name: str) -> None:
        row = self.wait_until_visible(self._record_row_locator(name))
        row.find_element(
            By.XPATH,
            ".//button[.//i[contains(@class, 'bi-pencil-fill')]]",
        ).click()
        self.wait_until_visible(self.save_button)

    def delete_record(self, name: str) -> None:
        row = self.wait_until_visible(self._record_row_locator(name))
        row.find_element(
            By.XPATH,
            ".//button[.//i[contains(@class, 'bi-trash')]]",
        ).click()
        self.click(self.delete_confirmation_button)
        self.wait.until(
            expected_conditions.invisibility_of_element_located(
                self._record_row_locator(name)
            )
        )

    @staticmethod
    def _record_row_locator(name: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//div[@role='row']"
            f"[.//*[normalize-space()='{name}']]",
        )


class PimReportsPage(BasePage):
    heading = (By.XPATH, "//h5[normalize-space()='Employee Reports']")
    add_button = (By.XPATH, "//button[normalize-space()='Add']")
    filter_toggle = (
        By.CSS_SELECTOR,
        ".oxd-table-filter-header-options button",
    )
    report_name_input = (
        By.XPATH,
        "//div[contains(@class, 'oxd-input-group')]"
        "[.//label[normalize-space()='Report Name']]//input",
    )
    search_button = (
        By.CSS_SELECTOR,
        "form.oxd-form button[type='submit']",
    )
    reset_button = (
        By.CSS_SELECTOR,
        ".oxd-table-filter-area button[type='reset']",
    )
    autocomplete_options = (By.CSS_SELECTOR, "[role='option']")
    no_records_message = (
        By.XPATH,
        "//*[normalize-space()='No Records Found']",
    )
    delete_confirmation_button = (
        By.XPATH,
        "//button[normalize-space()='Yes, Delete']",
    )

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.heading)

    def open_add_report(self) -> "PimReportFormPage":
        self.click(self.add_button)
        page = PimReportFormPage(self.driver)
        page.wait_until_loaded()
        return page

    def _ensure_filters_visible(self) -> None:
        if not any(
            element.is_displayed()
            for element in self.driver.find_elements(*self.report_name_input)
        ):
            self.click(self.filter_toggle)

    def search_by_report_name(self, report_name: str) -> bool:
        self._ensure_filters_visible()
        self.enter_text(self.report_name_input, report_name)

        def select_suggestion(driver: WebDriver) -> str | bool:
            for option in driver.find_elements(*self.autocomplete_options):
                if not option.is_displayed():
                    continue
                option_text = option.text.strip()
                if option_text == "No Records Found":
                    return "not found"
                if option_text == report_name:
                    option.click()
                    return "selected"
            return False

        suggestion_result = self.wait.until(select_suggestion)
        self.click(self.search_button)
        if suggestion_result == "not found":
            self.wait.until(
                expected_conditions.visibility_of_element_located(
                    self.no_records_message
                )
            )
            return False
        self.wait.until(
            lambda driver: self.has_report(report_name)
            or any(
                message.is_displayed()
                for message in driver.find_elements(*self.no_records_message)
            )
        )
        return self.has_report(report_name)

    def reset_filters(self) -> None:
        self.click(self.reset_button)
        self.wait.until(
            lambda driver: not driver.find_element(
                *self.report_name_input
            ).get_attribute("value")
        )

    def get_report_name_filter(self) -> str:
        return (
            self.wait_until_visible(self.report_name_input).get_attribute(
                "value"
            )
            or ""
        )

    def has_report(self, report_name: str) -> bool:
        return any(
            row.is_displayed()
            for row in self.driver.find_elements(
                *self._report_row_locator(report_name)
            )
        )

    def open_edit_report(self, report_name: str) -> "PimReportFormPage":
        row = self.wait_until_visible(self._report_row_locator(report_name))
        row.find_element(
            By.XPATH,
            ".//button[.//i[contains(@class, 'bi-pencil-fill')]]",
        ).click()
        page = PimReportFormPage(self.driver)
        page.wait_until_loaded()
        return page

    def run_report(self, report_name: str) -> str:
        row = self.wait_until_visible(self._report_row_locator(report_name))
        row.find_element(
            By.XPATH,
            ".//button[.//i[contains(@class, 'bi-file-text-fill')]]",
        ).click()
        report_heading = (
            By.XPATH,
            f"//h6[normalize-space()='{report_name}']",
        )
        return self.get_text(report_heading)

    def delete_report(self, report_name: str) -> None:
        row = self.wait_until_visible(self._report_row_locator(report_name))
        row.find_element(
            By.XPATH,
            ".//button[.//i[contains(@class, 'bi-trash')]]",
        ).click()
        self.click(self.delete_confirmation_button)
        self.wait.until(
            expected_conditions.invisibility_of_element_located(
                self._report_row_locator(report_name)
            )
        )

    @staticmethod
    def _report_row_locator(report_name: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//div[@role='row']"
            f"[.//*[normalize-space()='{report_name}']]",
        )


class PimReportFormPage(BasePage):
    report_heading = (By.XPATH, "//h6[normalize-space()='Add Report' or normalize-space()='Edit Report']")
    report_name_input = (
        By.XPATH,
        "//div[contains(@class, 'oxd-input-group')]"
        "[.//label[normalize-space()='Report Name']]//input",
    )
    save_button = (By.XPATH, "//button[normalize-space()='Save']")
    cancel_button = (By.XPATH, "//button[normalize-space()='Cancel']")
    validation_errors = (
        By.CSS_SELECTOR,
        ".oxd-input-field-error-message",
    )
    display_field_add_button = (
        By.XPATH,
        "//div[contains(@class, 'orangehrm-report-criteria')]"
        "[.//label[normalize-space()='Select Display Field']]//button",
    )

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.report_heading)

    def set_report_name(self, report_name: str) -> None:
        self.enter_text(self.report_name_input, report_name)

    def select_dropdown_option(self, label: str, option: str) -> None:
        option_locator = (
            By.XPATH,
            f"//*[@role='option' and normalize-space()='{option}']",
        )
        if not any(
            element.is_displayed()
            for element in self.driver.find_elements(*option_locator)
        ):
            self.click(self._dropdown_locator(label))
        self.click(option_locator)

    def get_dropdown_options(self, label: str) -> list[str]:
        dropdown_locator = self._dropdown_locator(label)
        self.click(dropdown_locator)
        options = self.wait_for_elements(
            (By.CSS_SELECTOR, "[role='option']"),
            minimum_count=1,
        )
        option_texts = [option.text.strip() for option in options]
        self.click(dropdown_locator)
        return option_texts

    def add_display_field(self, group: str, field: str) -> None:
        self.select_dropdown_option("Select Display Field Group", group)
        self.select_dropdown_option("Select Display Field", field)
        self.click(self.display_field_add_button)

    def save_empty_form(self) -> list[str]:
        self.click(self.save_button)
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

    def save_form(self, expected_report_name: str | None = None) -> None:
        self.click(self.save_button)
        reports_page = PimReportsPage(self.driver)
        if expected_report_name is not None:
            self.wait.until(
                expected_conditions.url_contains(
                    "/pim/displayPredefinedReport/"
                )
            )
            self.wait_until_visible(
                (
                    By.XPATH,
                    f"//h6[normalize-space()='{expected_report_name}']",
                )
            )
            self.click(PimPage.reports_link)
            reports_page.wait_until_loaded()
            self.wait.until(
                lambda driver: reports_page.has_report(expected_report_name)
            )
        else:
            reports_page.wait_until_loaded()

    def cancel_form(self) -> None:
        self.click(self.cancel_button)
        PimReportsPage(self.driver).wait_until_loaded()

    @staticmethod
    def _dropdown_locator(label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//div[contains(@class, 'oxd-input-group')]"
            f"[.//label[normalize-space()='{label}']]"
            "//div[contains(@class, 'oxd-select-text')]",
        )


class AddEmployeePage(BasePage):
    add_employee_heading = (
        By.XPATH,
        "//h6[normalize-space()='Add Employee' or normalize-space()='添加员工']",
    )
    first_name_input = (By.NAME, "firstName")
    middle_name_input = (By.NAME, "middleName")
    last_name_input = (By.NAME, "lastName")
    employee_id_input = (
        By.XPATH,
        "//label[normalize-space()='Employee Id' or "
        "normalize-space()='员工识别号']/parent::div/parent::div//input",
    )
    create_login_details_checkbox = (
        By.XPATH,
        "//p[normalize-space()='Create Login Details']"
        "/following::input[@type='checkbox']",
    )
    create_login_details_switch = (
        By.XPATH,
        "//p[normalize-space()='Create Login Details']"
        "/following::span[contains(@class, 'oxd-switch-input')]",
    )
    login_status_options = (
        By.XPATH,
        "//label[normalize-space()='Enabled' "
        "or normalize-space()='Disabled']",
    )
    save_button = (
        By.CSS_SELECTOR,
        "form.oxd-form button[type='submit']",
    )

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.add_employee_heading)

    def set_first_name(self, first_name: str) -> None:
        self.enter_text(self.first_name_input, first_name)

    def set_last_name(self, last_name: str) -> None:
        self.enter_text(self.last_name_input, last_name)

    def set_employee_id(self, employee_id: str) -> None:
        employee_id_field = self.wait_until_visible(self.employee_id_input)
        employee_id_field.send_keys(Keys.CONTROL, "a")
        employee_id_field.send_keys(employee_id)
        self.wait.until(
            lambda driver: driver.find_element(*self.employee_id_input).get_attribute(
                "value"
            )
            == employee_id
        )

    def enable_login_details(self) -> None:
        self.wait.until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".oxd-form-loader")
            )
        )
        checkbox = self.wait.until(
            lambda driver: driver.find_element(
                *self.create_login_details_checkbox
            )
        )
        if not checkbox.is_selected():
            self.click(self.create_login_details_switch)
        self.wait.until(
            lambda driver: driver.find_element(
                *self.create_login_details_checkbox
            ).is_selected()
        )

    def get_login_status_options(self) -> list[str]:
        self.wait.until(
            lambda driver: len(
                [
                    option
                    for option in driver.find_elements(
                        *self.login_status_options
                    )
                    if option.is_displayed()
                ]
            )
            == 2
        )
        return [
            option.text.strip()
            for option in self.driver.find_elements(*self.login_status_options)
            if option.is_displayed()
        ]

    def save(self) -> None:
        self.click(self.save_button)

    def get_validation_errors(self) -> list[str]:
        locator = (By.CSS_SELECTOR, ".oxd-input-field-error-message")
        self.wait.until(
            lambda driver: any(
                error.is_displayed() for error in driver.find_elements(*locator)
            )
        )
        return [
            error.text
            for error in self.driver.find_elements(*locator)
            if error.is_displayed()
        ]

    def add_employee(
        self,
        first_name: str,
        middle_name: str,
        last_name: str,
        employee_id: str,
    ) -> None:
        first_name_field = self.wait_until_visible(self.first_name_input)
        first_name_field.clear()
        first_name_field.send_keys(first_name)
        self.wait.until(
            lambda driver: first_name_field.get_attribute("value") == first_name
        )

        middle_name_field = self.wait_until_visible(self.middle_name_input)
        middle_name_field.clear()
        middle_name_field.send_keys(middle_name)
        self.wait.until(
            lambda driver: middle_name_field.get_attribute("value") == middle_name
        )

        last_name_field = self.wait_until_visible(self.last_name_input)
        last_name_field.clear()
        last_name_field.send_keys(last_name)
        self.wait.until(
            lambda driver: last_name_field.get_attribute("value") == last_name
        )

        employee_id_field = self.wait_until_visible(self.employee_id_input)
        employee_id_field.send_keys(Keys.CONTROL, "a")
        self.wait_until_visible(self.employee_id_input).send_keys(employee_id)
        self.wait.until(
            lambda driver: driver.find_element(*self.employee_id_input).get_attribute(
                "value"
            )
            == employee_id
        )
        self.click(self.save_button)
        self.wait.until(
            expected_conditions.url_contains("/pim/viewPersonalDetails/")
        )

        def employee_saved(driver: WebDriver) -> bool:
            try:
                if "/pim/viewPersonalDetails/" not in driver.current_url:
                    return False
                first_name_value = driver.find_element(*self.first_name_input).get_attribute("value")
                middle_name_value = driver.find_element(*self.middle_name_input).get_attribute("value")
                last_name_value = driver.find_element(*self.last_name_input).get_attribute("value")
                return (
                    first_name_value == first_name
                    and middle_name_value == middle_name
                    and last_name_value == last_name
                )
            except StaleElementReferenceException:
                return False

        self.wait.until(employee_saved)


class EmployeeDetailsPage(BasePage):
    first_name_input = (By.NAME, "firstName")
    middle_name_input = (By.NAME, "middleName")
    last_name_input = (By.NAME, "lastName")
    form_loader = (By.CSS_SELECTOR, ".oxd-form-loader")
    updated_message = (
        By.XPATH,
        "//*[normalize-space()='Successfully Updated']",
    )
    save_button = (
        By.CSS_SELECTOR,
        "form.oxd-form button[type='submit']",
    )

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def _wait_for_form_loaders(self) -> None:
        self.wait.until(
            expected_conditions.invisibility_of_element_located(
                self.form_loader
            )
        )

    def update_first_name(self, first_name: str) -> None:
        self._wait_for_form_loaders()
        self.wait.until(
            lambda driver: driver.find_element(
                *self.first_name_input
            ).get_attribute("value")
        )
        first_name_field = self.wait_until_visible(self.first_name_input)
        first_name_field.send_keys(Keys.CONTROL, "a")
        first_name_field.send_keys(Keys.BACKSPACE)
        self.wait.until(
            lambda driver: not driver.find_element(
                *self.first_name_input
            ).get_attribute("value")
        )
        first_name_field = self.wait_until_visible(self.first_name_input)
        first_name_field.send_keys(first_name)
        self.wait.until(
            lambda driver: self.wait_until_visible(
                self.first_name_input
            ).get_attribute("value")
            == first_name
        )
        self.click(self.save_button)
        self.wait_until_visible(self.updated_message)
        self._wait_for_form_loaders()

    def get_first_name(self) -> str:
        return self.wait_until_visible(self.first_name_input).get_attribute("value")

    def get_middle_name(self) -> str:
        return self.wait_until_visible(self.middle_name_input).get_attribute("value")

    def get_last_name(self) -> str:
        return self.wait_until_visible(self.last_name_input).get_attribute("value")
