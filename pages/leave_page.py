from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions

from pages.base_page import BasePage


class LeavePage(BasePage):
    leave_list_heading = (By.XPATH, "//h5[normalize-space()='Leave List']")
    apply_leave_heading = (By.XPATH, "//h6[normalize-space()='Apply Leave']")
    assign_leave_heading = (By.XPATH, "//h6[normalize-space()='Assign Leave']")
    form_loader = (By.CSS_SELECTOR, ".oxd-form-loader")
    add_entitlement_heading = (
        By.XPATH,
        "//p[normalize-space()='Add Leave Entitlement']",
    )
    my_leave_list_heading = (By.XPATH, "//h5[normalize-space()='My Leave List']")
    no_records_message = (By.XPATH, "//*[normalize-space()='No Records Found']")
    leave_balance = (By.CSS_SELECTOR, "p.orangehrm-leave-balance-text")
    leave_type_select = (
        By.XPATH,
        "//label[normalize-space()='Leave Type']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]"
        "//div[contains(@class, 'oxd-select-text')]",
    )
    from_date_input = (
        By.XPATH,
        "//label[normalize-space()='From Date']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//input",
    )
    to_date_input = (
        By.XPATH,
        "//label[normalize-space()='To Date']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//input",
    )
    comments_input = (
        By.XPATH,
        "//label[normalize-space()='Comments']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//textarea",
    )
    apply_leave_button = (
        By.XPATH,
        "//h6[normalize-space()='Apply Leave']"
        "/ancestor::div[contains(@class, 'orangehrm-card-container')]"
        "//button[@type='submit']",
    )
    validation_errors = (
        By.CSS_SELECTOR,
        "span.oxd-input-field-error-message",
    )
    application_error_toasts = (By.CSS_SELECTOR, ".oxd-toast-content")
    success_toast = (
        By.XPATH,
        "//div[contains(@class, 'oxd-toast-content')]"
        "//*[normalize-space()='Successfully Saved']",
    )
    entitlement_amount_input = (
        By.XPATH,
        "//label[normalize-space()='Entitlement']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//input",
    )
    entitlement_save_button = (
        By.XPATH,
        "//button[normalize-space()='Save']",
    )
    entitlement_update_dialog = (
        By.XPATH,
        "//div[@role='dialog']"
        "[.//*[normalize-space()='Updating Entitlement']]",
    )
    entitlement_confirm_button = (
        By.XPATH,
        "//div[@role='dialog']//button[normalize-space()='Confirm']",
    )
    my_leave_link = (
        By.XPATH,
        "//nav[@aria-label='Topbar Menu']//a[normalize-space()='My Leave']",
    )
    leave_rows = (By.CSS_SELECTOR, ".oxd-table-body [role='row']")
    employee_name_input = (
        By.XPATH,
        "//label[normalize-space()='Employee Name']/parent::div/parent::div//input",
    )
    employee_suggestions = (By.CSS_SELECTOR, "[role='option']")
    leave_status_filter = (
        By.XPATH,
        "//label[normalize-space()='Show Leave with Status']"
        "/parent::div/following-sibling::div"
        "//div[contains(@class, 'oxd-select-text--active') or "
        "contains(@class, 'oxd-select-text--focus')]",
    )
    selected_leave_statuses = (
        By.XPATH,
        "//label[normalize-space()='Show Leave with Status']"
        "/parent::div/following-sibling::div"
        "//span[contains(@class, 'oxd-multiselect-chips-selected')]",
    )
    selected_leave_status_clear_button = (
        By.XPATH,
        "//label[normalize-space()='Show Leave with Status']"
        "/parent::div/following-sibling::div"
        "//span[contains(@class, 'oxd-multiselect-chips-selected')]"
        "//i[contains(@class, '--clear')]",
    )
    search_button = (By.CSS_SELECTOR, "form.oxd-form button[type='submit']")
    reset_button = (By.CSS_SELECTOR, "form.oxd-form button[type='reset']")
    leave_list_link = (
        By.XPATH,
        "//nav[@aria-label='Sidepanel']//a[normalize-space()='Leave']",
    )
    apply_leave_link = (
        By.XPATH,
        "//nav[@aria-label='Topbar Menu']//a[normalize-space()='Apply']",
    )
    leave_submenu_categories: dict[str, tuple[str, str]] = {
        "Entitlements": (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']//li[.//*[normalize-space()='Entitlements']]",
        ),
        "Reports": (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']//li[.//*[normalize-space()='Reports']]",
        ),
        "Configure": (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']//li[.//*[normalize-space()='Configure']]",
        ),
        "More": (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']//li[.//*[normalize-space()='More']]",
        ),
    }
    leave_submenu_items: dict[tuple[str, str], tuple[str, str]] = {
        ("Entitlements", "Add Entitlements"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Add Entitlements']",
        ),
        ("Entitlements", "Employee Entitlements"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Employee Entitlements']",
        ),
        ("Reports", "Leave Entitlements and Usage Report"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Leave Entitlements and Usage Report']",
        ),
        ("Configure", "Leave Types"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Leave Types']",
        ),
        ("More", "Leave List"): (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']//a[normalize-space()='Leave List']",
        ),
        ("More", "Assign Leave"): (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']//a[normalize-space()='Assign Leave']",
        ),
    }
    leave_submenu_routes: dict[tuple[str, str], str] = {
        ("Entitlements", "Add Entitlements"): "/leave/addLeaveEntitlement",
        ("Entitlements", "Employee Entitlements"): "/leave/viewLeaveEntitlements",
        ("Reports", "Leave Entitlements and Usage Report"): (
            "/leave/viewLeaveBalanceReport"
        ),
        ("Configure", "Leave Types"): "/leave/leaveTypeList",
        ("More", "Leave List"): "/leave/viewLeaveList",
        ("More", "Assign Leave"): "/leave/assignLeave",
    }
    leave_topbar_links: dict[str, tuple[str, str]] = {
        "Apply": apply_leave_link,
        "My Leave": my_leave_link,
    }
    leave_topbar_routes: dict[str, str] = {
        "Apply": "/leave/applyLeave",
        "My Leave": "/leave/viewMyLeaveList",
    }
    assign_leave_button = (By.XPATH, "//button[normalize-space()='Assign']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def open_leave_list(self) -> None:
        self.click(self.leave_list_link)
        self.wait_until_loaded()

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.leave_list_heading)
        self.wait.until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, ".oxd-table")
            )
        )

    def get_leave_list_heading(self) -> str:
        return self.get_text(self.leave_list_heading)

    def set_employee_name_filter(self, employee_name: str) -> None:
        self.enter_text(self.employee_name_input, employee_name)

    def select_leave_status(self, status: str) -> None:
        self.click(self.leave_status_filter)
        option = (
            By.XPATH,
            f"//*[@role='option' and normalize-space()='{status}']",
        )
        self.click(option)

    def get_selected_leave_statuses(self) -> list[str]:
        return [
            status.text
            for status in self.driver.find_elements(
                *self.selected_leave_statuses
            )
        ]

    def reset_filters(self) -> None:
        self.click(self.reset_button)
        while selected_statuses := self.driver.find_elements(
            *self.selected_leave_statuses
        ):
            selected_count = len(selected_statuses)
            self.click(self.selected_leave_status_clear_button)
            self.wait.until(
                lambda driver: len(
                    driver.find_elements(*self.selected_leave_statuses)
                )
                < selected_count
            )

    def search_leave_list(self) -> list[str]:
        self.click(self.search_button)

        def results_loaded(driver: WebDriver) -> bool:
            try:
                return bool(
                    driver.find_elements(
                        By.CSS_SELECTOR,
                        ".oxd-table-body [role='row']",
                    )
                ) or any(
                    message.is_displayed()
                    for message in driver.find_elements(*self.no_records_message)
                )
            except StaleElementReferenceException:
                return False

        self.wait.until(results_loaded)
        rows = self.driver.find_elements(
            By.CSS_SELECTOR, ".oxd-table-body [role='row']"
        )
        if not rows:
            return []

        headers = self.driver.find_elements(
            By.CSS_SELECTOR, ".oxd-table-header [role='columnheader']"
        )
        status_column = next(
            (
                index
                for index, header in enumerate(headers)
                if header.text.strip() == "Status"
            ),
            None,
        )
        if status_column is None:
            raise RuntimeError("Could not find the Status column in the Leave List.")

        statuses = []
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "[role='cell']")
            if status_column >= len(cells):
                raise RuntimeError("Leave List row has no cell for the Status column.")
            status = cells[status_column].text
            statuses.append(status.partition(" (")[0])
        return statuses

    def open_apply_leave(self) -> None:
        self.open_leave_topbar_item("Apply")
        self.wait_until_visible(self.apply_leave_heading)
        self.wait.until(
            expected_conditions.invisibility_of_element_located(self.form_loader)
        )

    def open_leave_topbar_item(self, item: str) -> None:
        self.click(self.leave_topbar_links[item])
        self.wait.until(
            expected_conditions.url_contains(self.leave_topbar_routes[item])
        )

    def open_leave_submenu_item(self, category: str, item: str) -> None:
        key = (category, item)
        self.click(self.leave_submenu_categories[category])
        self.click(self.leave_submenu_items[key])
        self.wait.until(
            expected_conditions.url_contains(self.leave_submenu_routes[key])
        )

    def open_assign_leave(self) -> None:
        self.open_leave_submenu_item("More", "Assign Leave")
        self.wait_until_visible(self.assign_leave_heading)

    def ensure_leave_entitlement(
        self,
        employee_name: str,
        leave_type: str,
        amount: int,
    ) -> None:
        employee_name = " ".join(employee_name.split())
        self.open_leave_submenu_item("Entitlements", "Add Entitlements")
        self.wait_until_visible(self.add_entitlement_heading)
        self.enter_text(self.employee_name_input, employee_name)

        requested_name = " ".join(employee_name.split())
        requested_name_parts = set(requested_name.casefold().split())

        def find_employee_suggestion(driver: WebDriver) -> WebElement | bool:
            try:
                options = [
                    option
                    for option in driver.find_elements(*self.employee_suggestions)
                    if option.is_displayed()
                ]
                exact_matches = [
                    option
                    for option in options
                    if " ".join(option.text.split()).casefold()
                    == requested_name.casefold()
                ]
                matches = exact_matches or [
                    option
                    for option in options
                    if requested_name_parts.issubset(
                        set(" ".join(option.text.split()).casefold().split())
                    )
                ]
                if len(matches) > 1:
                    raise RuntimeError(
                        f"Employee name {employee_name!r} matches multiple "
                        "suggestions. Set LEAVE_TEST_EMPLOYEE_NAME to a name "
                        "that matches one employee, or use an isolated test "
                        "account."
                    )
                return matches[0] if matches else False
            except StaleElementReferenceException:
                return False

        employee_option = self.wait.until(find_employee_suggestion)
        selected_employee_name = " ".join(employee_option.text.split())
        employee_option.click()
        self.wait.until(
            lambda driver: driver.find_element(
                *self.employee_name_input
            ).get_attribute("value")
            == selected_employee_name
        )
        self.click(self.leave_type_select)
        leave_type_option = (
            By.XPATH,
            f"//*[@role='option' and normalize-space()='{leave_type}']",
        )
        self.click(leave_type_option)
        self.enter_text(self.entitlement_amount_input, str(amount))
        self.click(self.entitlement_save_button)

        def save_result(driver: WebDriver) -> str | bool:
            dialog = driver.find_elements(*self.entitlement_update_dialog)
            if dialog and dialog[0].is_displayed():
                return "confirm"
            toast = driver.find_elements(*self.success_toast)
            if toast and toast[0].is_displayed():
                return "saved"
            return False

        result = self.wait.until(save_result)
        if result == "confirm":
            self.click(self.entitlement_confirm_button)
            self.wait_until_visible(self.success_toast)

    def select_leave_type(self, leave_type: str) -> None:
        self.click(self.leave_type_select)
        option = (
            By.XPATH,
            f"//*[@role='option' and normalize-space()='{leave_type}']",
        )
        self.click(option)

    def set_leave_dates(self, from_date: str, to_date: str) -> None:
        for locator, value in (
            (self.from_date_input, from_date),
            (self.to_date_input, to_date),
        ):
            self.wait.until(
                expected_conditions.invisibility_of_element_located(
                    self.form_loader
                )
            )
            element = self.wait_until_visible(locator)
            element.click()
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.BACKSPACE)
            element.send_keys(value)
            self.wait.until(
                lambda driver: driver.find_element(*locator).get_attribute(
                    "value"
                )
                == value
            )

    def set_leave_comments(self, comments: str) -> None:
        self.enter_text(self.comments_input, comments)

    def submit_leave_application(self) -> None:
        self.click(self.apply_leave_button)

    def submit_assign_leave(self) -> None:
        self.click(self.assign_leave_button)

    def get_application_validation_errors(self) -> list[str]:
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

    def wait_for_application_result(self) -> str:
        def find_application_result(driver: WebDriver) -> str | bool:
            try:
                return next(
                    (
                        toast.text
                        for toast in driver.find_elements(
                            *self.application_error_toasts
                        )
                        if toast.is_displayed() and toast.text.strip()
                    ),
                    False,
                )
            except StaleElementReferenceException:
                return False

        return self.wait.until(find_application_result)

    def get_application_success_message(self) -> str:
        def find_application_result(driver: WebDriver) -> str | bool:
            try:
                for success in driver.find_elements(*self.success_toast):
                    if success.is_displayed():
                        return success.text
                for toast in driver.find_elements(
                    *self.application_error_toasts
                ):
                    if toast.is_displayed() and toast.text.strip():
                        return toast.text
            except StaleElementReferenceException:
                return False
            return False

        return self.wait.until(find_application_result)

    def open_my_leave_list(self) -> None:
        self.open_leave_topbar_item("My Leave")
        self.wait_until_visible(self.my_leave_list_heading)

    def get_my_leave_rows(self) -> list[str]:
        self.wait.until(
            lambda driver: any(
                row.is_displayed()
                for row in driver.find_elements(*self.leave_rows)
            )
            or any(
                message.is_displayed()
                for message in driver.find_elements(*self.no_records_message)
            )
        )
        return [
            row.text
            for row in self.driver.find_elements(*self.leave_rows)
            if row.is_displayed()
        ]

    def is_no_records_message_displayed(self) -> bool:
        return any(
            message.is_displayed()
            for message in self.driver.find_elements(*self.no_records_message)
        )

    def wait_for_my_leave_application(self, comment: str) -> bool:
        def application_is_visible(driver: WebDriver) -> bool:
            try:
                return any(
                    comment in row.text and "Pending Approval" in row.text
                    for row in driver.find_elements(*self.leave_rows)
                    if row.is_displayed()
                )
            except StaleElementReferenceException:
                return False

        return self.wait.until(application_is_visible)

    def get_leave_balance(self) -> str:
        return self.get_text(self.leave_balance)
