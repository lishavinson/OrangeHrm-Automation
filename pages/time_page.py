from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions

from config.config import BASE_URL
from pages.base_page import BasePage


class TimePage(BasePage):
    topbar_menu = (By.CSS_SELECTOR, "nav[aria-label='Topbar Menu']")
    select_employee_heading = (By.XPATH, "//h6[normalize-space()='Select Employee']")
    validation_errors = (By.CSS_SELECTOR, "span.oxd-input-field-error-message")
    employee_name_input = (By.CSS_SELECTOR, "input[placeholder='Type for hints...']")
    employee_suggestions = (By.CSS_SELECTOR, "[role='option']")
    employee_timesheet_view_button = (
        By.CSS_SELECTOR,
        "form.oxd-form button[type='submit']",
    )
    pending_timesheet_rows = (By.CSS_SELECTOR, ".oxd-table-body [role='row']")
    no_records_message = (By.XPATH, "//*[normalize-space()='No Records Found']")
    timesheet_detail_heading = (
        By.XPATH,
        "//h6[starts-with(normalize-space(), 'Timesheet for ')]",
    )
    add_button = (By.XPATH, "//button[normalize-space()='Add']")
    save_button = (By.XPATH, "//button[normalize-space()='Save']")
    project_report_view_button = (
        By.CSS_SELECTOR,
        "form.oxd-form button[type='submit']",
    )
    punch_in_date_input = (By.CSS_SELECTOR, "input[placeholder='yyyy-dd-mm']")
    punch_in_time_input = (By.CSS_SELECTOR, "input[placeholder='hh:mm']")
    punch_in_button = (By.XPATH, "//button[normalize-space()='In']")

    submenu_categories: dict[str, tuple[str, str]] = {
        "Timesheets": (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']//li[.//*[normalize-space()='Timesheets']]",
        ),
        "Attendance": (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']//li[.//*[normalize-space()='Attendance']]",
        ),
        "Reports": (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']//li[.//*[normalize-space()='Reports']]",
        ),
        "Project Info": (
            By.XPATH,
            "//nav[@aria-label='Topbar Menu']//li[.//*[normalize-space()='Project Info']]",
        ),
    }
    submenu_items: dict[tuple[str, str], tuple[str, str]] = {
        ("Timesheets", "My Timesheets"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='My Timesheets']",
        ),
        ("Timesheets", "Employee Timesheets"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Employee Timesheets']",
        ),
        ("Attendance", "My Records"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='My Records']",
        ),
        ("Attendance", "Punch In/Out"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Punch In/Out']",
        ),
        ("Attendance", "Employee Records"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Employee Records']",
        ),
        ("Attendance", "Configuration"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Configuration']",
        ),
        ("Reports", "Project Reports"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Project Reports']",
        ),
        ("Reports", "Employee Reports"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Employee Reports']",
        ),
        ("Reports", "Attendance Summary"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Attendance Summary']",
        ),
        ("Project Info", "Customers"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Customers']",
        ),
        ("Project Info", "Projects"): (
            By.XPATH,
            "//*[@role='menuitem' and normalize-space()='Projects']",
        ),
    }
    submenu_routes: dict[tuple[str, str], str] = {
        ("Timesheets", "My Timesheets"): "/time/viewMyTimesheet",
        ("Timesheets", "Employee Timesheets"): "/time/viewEmployeeTimesheet",
        ("Attendance", "My Records"): "/attendance/viewMyAttendanceRecord",
        ("Attendance", "Punch In/Out"): "/attendance/punchIn",
        ("Attendance", "Employee Records"): "/attendance/viewAttendanceRecord",
        ("Attendance", "Configuration"): "/attendance/configure",
        ("Reports", "Project Reports"): "/time/displayProjectReportCriteria",
        ("Reports", "Employee Reports"): "/time/displayEmployeeReportCriteria",
        ("Reports", "Attendance Summary"): (
            "/time/displayAttendanceSummaryReportCriteria"
        ),
        ("Project Info", "Customers"): "/time/viewCustomers",
        ("Project Info", "Projects"): "/time/viewProjects",
    }

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def open_time_module(self) -> None:
        self.driver.get(f"{BASE_URL}/web/index.php/time/viewTimeModule")
        self.wait_until_loaded()

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.topbar_menu)
        self.wait_until_visible(self.select_employee_heading)

    def open_submenu_item(self, category: str, item: str) -> None:
        key = (category, item)
        self.click(self.submenu_categories[category])
        self.click(self.submenu_items[key])
        self.wait.until(
            expected_conditions.url_contains(self.submenu_routes[key])
        )

    def is_heading_visible(self, heading: str) -> bool:
        locator = (
            By.XPATH,
            f"//h5[normalize-space()='{heading}']"
            f" | //h6[normalize-space()='{heading}']",
        )
        return self.is_visible(locator)

    def get_timesheet_detail_heading(self) -> str:
        return self.get_text(self.timesheet_detail_heading)

    def get_pending_timesheet_employee_names(self) -> list[str]:
        def list_loaded(driver: WebDriver) -> bool:
            try:
                return any(
                    row.is_displayed()
                    for row in driver.find_elements(*self.pending_timesheet_rows)
                ) or any(
                    message.is_displayed()
                    for message in driver.find_elements(*self.no_records_message)
                )
            except StaleElementReferenceException:
                return False

        self.wait.until(list_loaded)
        employee_names = []
        for row in self.driver.find_elements(*self.pending_timesheet_rows):
            try:
                if not row.is_displayed():
                    continue
                cells = row.find_elements(By.CSS_SELECTOR, "[role='cell']")
                if not cells:
                    continue
                employee_cell = " ".join(cells[0].text.split())
                prefix = "Employee Name "
                if employee_cell.startswith(prefix):
                    employee_names.append(employee_cell[len(prefix) :])
            except StaleElementReferenceException:
                continue
        return employee_names

    def set_employee_name_filter(self, employee_name: str) -> None:
        self.enter_text(self.employee_name_input, employee_name)

    def select_employee_suggestion(self, employee_name: str) -> None:
        expected_name = " ".join(employee_name.split())

        def choose_suggestion(driver: WebDriver) -> WebElement | bool:
            try:
                for option in driver.find_elements(*self.employee_suggestions):
                    if (
                        option.is_displayed()
                        and " ".join(option.text.split()) == expected_name
                    ):
                        return option
            except StaleElementReferenceException:
                return False
            return False

        self.wait.until(choose_suggestion).click()
        self.wait.until(
            lambda driver: " ".join(
                (driver.find_element(*self.employee_name_input).get_attribute("value") or "").split()
            )
            == expected_name
        )

    def view_employee_timesheet(self) -> None:
        self.click(self.employee_timesheet_view_button)
        self.wait.until(
            lambda driver: "/time/viewTimesheet/employeeId/" in driver.current_url
            or any(
                error.is_displayed()
                for error in driver.find_elements(*self.validation_errors)
            )
        )
        if "/time/viewTimesheet/employeeId/" in self.driver.current_url:
            self.wait_until_visible(self.timesheet_detail_heading)

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

    def open_add_customer_form(self) -> None:
        self.open_submenu_item("Project Info", "Customers")
        self.click(self.add_button)
        self.wait.until(expected_conditions.url_contains("/time/addCustomer"))
        self.is_heading_visible("Add Customer")

    def open_add_project_form(self) -> None:
        self.open_submenu_item("Project Info", "Projects")
        self.click(self.add_button)
        self.wait.until(expected_conditions.url_contains("/time/saveProject"))
        self.is_heading_visible("Add Project")

    def save_form(self) -> None:
        self.click(self.save_button)

    def view_project_report(self) -> None:
        self.click(self.project_report_view_button)

    def is_punch_in_form_visible(self) -> bool:
        return all(
            self.is_visible(locator)
            for locator in (
                self.punch_in_date_input,
                self.punch_in_time_input,
                self.punch_in_button,
            )
        )

    def is_employee_attendance_search_form_visible(self) -> bool:
        return all(
            self.is_visible(locator)
            for locator in (
                self.employee_name_input,
                self.punch_in_date_input,
            )
        ) and bool(
            self.driver.find_elements(
                By.CSS_SELECTOR,
                "form.oxd-form button[type='submit']",
            )
        )

    def is_my_timesheet_period_visible(self) -> bool:
        return self.is_visible(self.punch_in_date_input)
