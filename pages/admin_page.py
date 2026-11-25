from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions

from pages.base_page import BasePage


class AdminPage(BasePage):
    system_users_heading = (By.XPATH, "//h5[normalize-space()='System Users']")
    filter_panel_toggle = (
        By.XPATH,
        "//h5[normalize-space()='System Users']"
        "/ancestor::div[contains(@class, 'oxd-table-filter-header')]//button",
    )
    filter_form = (By.CSS_SELECTOR, "form.oxd-form")
    employee_name_input = (
        By.CSS_SELECTOR,
        "input[placeholder='Type for hints...']",
    )
    dropdown_options = (By.CSS_SELECTOR, "[role='option']")
    employee_name_suggestion = (
        By.XPATH,
        "//*[@role='option' and normalize-space()!='Searching....']",
    )
    search_button = (
        By.XPATH,
        "//form//button[@type='submit' and normalize-space()='Search']",
    )
    reset_button = (
        By.XPATH,
        "//form//button[@type='button' and normalize-space()='Reset']",
    )
    user_rows = (By.CSS_SELECTOR, "[role='row']")
    mobile_user_cards = (By.CSS_SELECTOR, ".oxd-table-card")
    table_headers = (By.CSS_SELECTOR, "[role='columnheader']")
    no_records_message = (By.XPATH, "//*[normalize-space()='No Records Found']")
    records_summary = (
        By.CSS_SELECTOR,
        ".orangehrm-horizontal-padding .oxd-text--span",
    )
    add_user_button = (
        By.XPATH,
        "//button[contains(normalize-space(.), 'Add')]",
    )
    topbar_navigation = (By.XPATH, "//nav[@aria-label='Topbar Menu']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.system_users_heading)
        if not self.driver.find_elements(*self.filter_form):
            self.click(self.filter_panel_toggle)
        self.wait_until_visible(self.filter_form)
        self.wait.until(
            lambda driver: driver.find_elements(*self.records_summary)
            or driver.find_elements(*self.no_records_message)
        )

    def get_heading(self) -> str:
        return self.get_text(self.system_users_heading)

    def is_filter_control_visible(self, label: str) -> bool:
        if label == "Employee Name":
            locator = self.employee_name_input
        elif label in {"User Role", "Status"}:
            locator = self._dropdown_locator(label)
        else:
            locator = self._input_locator(label)
        return self.is_visible(locator)

    def get_dropdown_options(self, label: str) -> list[str]:
        self.click(self._dropdown_locator(label))
        options = self.wait_for_elements(self.dropdown_options, minimum_count=1)
        option_texts = [option.text.strip() for option in options]
        self.click(
            (
                By.XPATH,
                "//*[@role='option' and normalize-space()='-- Select --']",
            )
        )
        return option_texts

    def set_username_filter(self, username: str) -> None:
        self.enter_text(self._input_locator("Username"), username)

    def set_employee_name_filter(self, employee_name: str) -> None:
        self.enter_text(self.employee_name_input, employee_name)
        self.wait.until(
            lambda driver: any(
                option.text.strip() != "Searching...."
                for option in driver.find_elements(*self.dropdown_options)
            )
        )
        self.click(self.employee_name_suggestion)

    def select_user_role(self, role: str) -> None:
        self._select_dropdown_option("User Role", role)

    def select_status(self, status: str) -> None:
        self._select_dropdown_option("Status", status)

    def search(self, expected_result_count: int | None = None) -> None:
        self.click(self.search_button)
        if expected_result_count is not None:
            self.wait.until(
                lambda driver: len(self.get_user_rows())
                == expected_result_count
            )

    def search_for_no_results(self) -> None:
        self.click(self.search_button)
        self.wait_until_visible(self.no_records_message)

    def reset_filters(self, expected_summary: str | None = None) -> None:
        self.click(self.reset_button)
        if expected_summary is not None:
            self.wait.until(
                expected_conditions.text_to_be_present_in_element(
                    self.records_summary,
                    expected_summary,
                )
            )

    def get_filter_values(self) -> dict[str, str]:
        return {
            "Username": self.wait_until_visible(
                self._input_locator("Username")
            ).get_attribute("value")
            or "",
            "Employee Name": self.wait_until_visible(
                self.employee_name_input
            ).get_attribute("value")
            or "",
            "User Role": self.get_text(self._dropdown_text_locator("User Role")),
            "Status": self.get_text(self._dropdown_text_locator("Status")),
        }

    def get_user_rows(self) -> list[WebElement]:
        rows = [
            row
            for row in self.driver.find_elements(*self.user_rows)
            if row.is_displayed()
            and not row.find_elements(*self.table_headers)
            and row.find_elements(By.CSS_SELECTOR, "[role='cell']")
        ]
        if rows:
            return rows
        return [
            card
            for card in self.driver.find_elements(*self.mobile_user_cards)
            if card.is_displayed()
        ]

    def get_usernames(self) -> list[str]:
        usernames = []
        for row in self.get_user_rows():
            username = self._get_row_values(row).get("Username")
            if username:
                usernames.append(username)
        return usernames

    def get_user_field(self, username: str, field: str) -> str:
        for row in self.get_user_rows():
            values = self._get_row_values(row)
            if values.get("Username") == username:
                if field not in values:
                    raise ValueError(
                        f"User card {username!r} does not have field {field!r}."
                    )
                return values[field]
        raise LookupError(f"User {username!r} was not found in the visible list.")

    def get_user_action_count(self, username: str) -> int:
        for row in self.get_user_rows():
            if self._get_row_values(row).get("Username") == username:
                return len(
                    row.find_elements(
                        By.CSS_SELECTOR,
                        "button.oxd-icon-button",
                    )
                )
        raise LookupError(f"User {username!r} was not found in the visible list.")

    def get_records_summary(self) -> str:
        return self.get_text(self.records_summary).strip()

    def open_add_user(self) -> "AddUserPage":
        self.click(self.add_user_button)
        page = AddUserPage(self.driver)
        page.wait_until_loaded()
        return page

    def open_subcategory(
        self,
        category: str,
        item: str,
        expected_heading: str,
    ) -> None:
        if category == "More":
            item_locator = (
                By.XPATH,
                f"{self.topbar_navigation[1]}//a"
                f"[contains(normalize-space(.), '{item}')]",
            )
            visible_items = [
                element
                for element in self.driver.find_elements(*item_locator)
                if element.is_displayed()
            ]
            if not visible_items:
                self.click(
                    (
                        By.XPATH,
                        f"{self.topbar_navigation[1]}"
                        "//span[normalize-space()='More']",
                    )
                )
        else:
            self.click(
                (
                    By.XPATH,
                    f"{self.topbar_navigation[1]}"
                    f"//span[normalize-space()='{category}']",
                )
            )
            item_locator = (
                By.XPATH,
                f"{self.topbar_navigation[1]}//*[@role='menuitem'"
                f" and normalize-space()='{item}']",
            )
        self.click(item_locator)
        self.wait_until_visible(
            (
                By.XPATH,
                "//*[self::h5 or self::h6]"
                f"[normalize-space()='{expected_heading}']",
            )
        )

    def _select_dropdown_option(self, label: str, option: str) -> None:
        self.click(self._dropdown_locator(label))
        self.click(
            (
                By.XPATH,
                f"//*[@role='option' and normalize-space()='{option}']",
            )
        )

    @staticmethod
    def _input_locator(label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//form//div[contains(@class, 'oxd-input-group')]"
            f"[.//label[normalize-space()='{label}']]//input",
        )

    @staticmethod
    def _dropdown_locator(label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//form//div[contains(@class, 'oxd-input-group')]"
            f"[.//label[normalize-space()='{label}']]"
            "//div[contains(@class, 'oxd-select-text')]",
        )

    @staticmethod
    def _dropdown_text_locator(label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//form//div[contains(@class, 'oxd-input-group')]"
            f"[.//label[normalize-space()='{label}']]"
            "//div[contains(@class, 'oxd-select-text-input')]",
        )

    def _get_row_values(self, row: WebElement) -> dict[str, str]:
        values: dict[str, str] = {}
        card_cells = row.find_elements(
            By.CSS_SELECTOR,
            ".oxd-table-card-cell",
        )
        if card_cells:
            for cell in card_cells:
                header = cell.find_element(
                    By.CSS_SELECTOR,
                    ".header",
                ).text.strip()
                value = cell.find_element(
                    By.CSS_SELECTOR,
                    ".data",
                ).text.strip()
                values[header] = value
            return values

        headers = self.driver.find_elements(*self.table_headers)
        cells = row.find_elements(By.CSS_SELECTOR, "[role='cell']")
        known_fields = {"Username", "User Role", "Employee Name", "Status"}
        for header, cell in zip(headers, cells):
            header_text = header.text.strip()
            field = next(
                (name for name in known_fields if header_text.startswith(name)),
                None,
            )
            if field is not None:
                values[field] = cell.text.strip()
        return values


class AddUserPage(BasePage):
    heading = (By.XPATH, "//h6[normalize-space()='Add User']")
    save_button = (By.XPATH, "//button[normalize-space()='Save']")
    cancel_button = (By.XPATH, "//button[normalize-space()='Cancel']")
    validation_messages = (
        By.XPATH,
        "//*[normalize-space()='Required' "
        "or normalize-space()='Passwords do not match']",
    )
    system_users_heading = (By.XPATH, "//h5[normalize-space()='System Users']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.heading)

    def save(self) -> None:
        self.click(self.save_button)

    def cancel(self) -> None:
        self.click(self.cancel_button)

    def get_validation_messages(self) -> list[str]:
        messages = self.wait_for_elements(
            self.validation_messages,
            minimum_count=1,
        )
        return [message.text.strip() for message in messages]

    def is_back_on_system_users(self) -> bool:
        return self.is_visible(self.system_users_heading)


class AdminSubcategoryFormPage(BasePage):
    add_button = (By.XPATH, "//button[normalize-space()='Add']")
    save_button = (By.XPATH, "//button[normalize-space()='Save']")
    cancel_button = (By.XPATH, "//button[normalize-space()='Cancel']")
    required_message = (By.XPATH, "//*[normalize-space()='Required']")
    form_field_labels = (
        By.XPATH,
        "//div[contains(@class, 'oxd-input-group')]//label",
    )
    delete_confirmation_button = (
        By.XPATH,
        "//button[normalize-space()='Yes, Delete']",
    )

    def __init__(self, driver: WebDriver, heading: str) -> None:
        super().__init__(driver)
        self.heading = (
            By.XPATH,
            "//*[self::h5 or self::h6]"
            f"[normalize-space()='{heading}']",
        )

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.heading)

    def open_add_form(self) -> None:
        self.wait.until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".oxd-form-loader")
            )
        )
        self.click(self.add_button)
        self.wait_until_visible(self.save_button)
        self.wait.until(
            lambda driver: driver.find_elements(*self.form_field_labels)
        )

    def get_form_field_labels(self) -> list[str]:
        return [
            label.text.strip()
            for label in self.driver.find_elements(*self.form_field_labels)
            if label.is_displayed()
        ]

    def save_empty_form(self) -> list[str]:
        self.click(self.save_button)
        self.wait.until(
            lambda driver: any(
                message.is_displayed()
                for message in driver.find_elements(*self.required_message)
            )
        )
        return [
            message.text.strip()
            for message in self.driver.find_elements(*self.required_message)
            if message.is_displayed()
        ]

    @staticmethod
    def _label_variants(label: str) -> tuple[str, ...]:
        if label == "Notes":
            return ("Notes", "Note")
        if label == "Note":
            return ("Note", "Notes")
        return (label,)

    def set_field(self, label: str, value: str) -> None:
        dropdowns = self.driver.find_elements(*self._dropdown_locator(label))
        if dropdowns:
            self.click(self._dropdown_locator(label))
            self.click(
                (
                    By.XPATH,
                    f"//*[@role='option' and normalize-space()='{value}']",
                )
            )
            return
        self.enter_text(self._field_locator(label), value)

    def set_fields(self, fields: dict[str, str]) -> None:
        for label, value in fields.items():
            self.set_field(label, value)

    def get_field_value(self, label: str) -> str:
        dropdowns = self.driver.find_elements(*self._dropdown_locator(label))
        if dropdowns:
            return self.get_text(self._dropdown_text_locator(label))
        return (
            self.wait_until_visible(self._field_locator(label)).get_attribute(
                "value"
            )
            or ""
        )

    def save_form(self, expected_name: str | None = None) -> None:
        self.click(self.save_button)
        self.wait_until_visible(self.heading)
        self.wait_until_visible(self.add_button)
        if expected_name is not None:
            self.wait.until(lambda driver: self.has_record(expected_name))

    def cancel_form(self) -> None:
        self.click(self.cancel_button)
        self.wait_until_visible(self.add_button)

    def has_record(self, name: str) -> bool:
        return any(
            row.is_displayed()
            for row in self.driver.find_elements(*self._record_row_locator(name))
        )

    def open_edit_form(self, name: str) -> None:
        row = self.wait_until_visible(self._record_row_locator(name))
        row.find_element(
            By.XPATH,
            ".//button[.//i[contains(@class, 'bi-pencil-fill')]]",
        ).click()
        self.wait_until_visible(self.save_button)
        self.wait.until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".oxd-form-loader")
            )
        )

    def delete_record(self, name: str) -> None:
        row_locator = self._record_row_locator(name)
        row = self.wait_until_visible(row_locator)
        row.find_element(
            By.XPATH,
            ".//button[.//i[contains(@class, 'bi-trash')]]",
        ).click()
        self.click(self.delete_confirmation_button)
        self.wait.until(
            expected_conditions.invisibility_of_element_located(row_locator)
        )

    @staticmethod
    def _field_locator(label: str) -> tuple[str, str]:
        variants = AdminSubcategoryFormPage._label_variants(label)
        label_predicate = " or ".join(
            f"normalize-space()='{variant}'" for variant in variants
        )
        return (
            By.XPATH,
            "//div[contains(@class, 'oxd-input-group')]"
            f"[.//label[{label_predicate}]]"
            "//*[self::input or self::textarea]",
        )

    @staticmethod
    def _dropdown_locator(label: str) -> tuple[str, str]:
        variants = AdminSubcategoryFormPage._label_variants(label)
        label_predicate = " or ".join(
            f"normalize-space()='{variant}'" for variant in variants
        )
        return (
            By.XPATH,
            "//div[contains(@class, 'oxd-input-group')]"
            f"[.//label[{label_predicate}]]"
            "//div[contains(@class, 'oxd-select-text')]",
        )

    @staticmethod
    def _dropdown_text_locator(label: str) -> tuple[str, str]:
        variants = AdminSubcategoryFormPage._label_variants(label)
        label_predicate = " or ".join(
            f"normalize-space()='{variant}'" for variant in variants
        )
        return (
            By.XPATH,
            "//div[contains(@class, 'oxd-input-group')]"
            f"[.//label[{label_predicate}]]"
            "//div[contains(@class, 'oxd-select-text-input')]",
        )

    @staticmethod
    def _record_row_locator(name: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//div[@role='row']"
            f"[.//*[normalize-space()='{name}']]",
        )


class GeneralInformationPage(BasePage):
    edit_toggle = (
        By.XPATH,
        "//label[normalize-space()='Edit']",
    )
    save_button = (By.XPATH, "//button[normalize-space()='Save']")
    field_labels = (By.XPATH, "//form//label")

    def get_field_labels(self) -> list[str]:
        return [
            label.text.strip()
            for label in self.driver.find_elements(*self.field_labels)
            if label.is_displayed() and label.text.strip() != "Edit"
        ]

    def enable_edit_mode(self) -> None:
        self.click(self.edit_toggle)
        self.wait_until_visible(self.save_button)

    def is_save_button_visible(self) -> bool:
        return self.is_visible(self.save_button)


class OrganizationStructurePage(BasePage):
    heading = (
        By.XPATH,
        "//h6[normalize-space()='Organization Structure']",
    )
    hierarchy_controls = (
        By.CSS_SELECTOR,
        "form, [role='tree'], [role='treeitem']",
    )

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.heading)

    def get_visible_hierarchy_controls(self) -> list[WebElement]:
        return [
            element
            for element in self.driver.find_elements(*self.hierarchy_controls)
            if element.is_displayed()
        ]


class CorporateBrandingPage(BasePage):
    preview_button = (By.XPATH, "//button[normalize-space()='Preview']")
    field_labels = (By.XPATH, "//form//label")

    def get_field_labels(self) -> list[str]:
        return [
            label.text.strip()
            for label in self.driver.find_elements(*self.field_labels)
            if label.is_displayed() and label.text.strip()
        ]

    def preview(self) -> None:
        self.wait.until(
            expected_conditions.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".oxd-form-loader")
            )
        )
        self.click(self.preview_button)
        self.wait.until(expected_conditions.url_contains("/admin/addTheme"))
