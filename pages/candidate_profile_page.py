from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions

from pages.base_page import BasePage


class CandidateProfilePage(BasePage):
    profile_heading = (By.XPATH, "//h6[normalize-space()='Candidate Profile']")
    shortlist_heading = (By.XPATH, "//h6[normalize-space()='Shortlist Candidate']")
    first_name_input = (By.NAME, "firstName")
    last_name_input = (By.NAME, "lastName")
    email_input = (
        By.XPATH,
        "//label[normalize-space()='Email']"
        "/ancestor::div[contains(@class, 'oxd-input-group')]//input",
    )
    edit_toggle = (
        By.XPATH,
        "//label[normalize-space()='Edit']",
    )
    save_button = (By.XPATH, "//button[normalize-space()='Save']")
    update_success_message = (
        By.XPATH,
        "//*[normalize-space()='Successfully Updated']",
    )
    toast_content = (By.CSS_SELECTOR, ".oxd-toast-content")
    status_text = (
        By.XPATH,
        "//p[contains(@class, 'oxd-text--subtitle-2')"
        " and starts-with(normalize-space(), 'Status:')]",
    )
    shortlist_button = (By.XPATH, "//button[normalize-space()='Shortlist']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.profile_heading)

    def enable_editing(self) -> None:
        self.click(self.edit_toggle)
        self.wait.until(
            expected_conditions.element_to_be_clickable(self.first_name_input)
        )

    def update_first_name(self, first_name: str) -> None:
        self.enter_text(self.first_name_input, first_name)

    def save(self) -> None:
        self.click(self.save_button)
        self.wait_until_visible(self.update_success_message)

    def get_first_name(self) -> str:
        return self.wait_until_visible(self.first_name_input).get_attribute(
            "value"
        ) or ""

    def get_status(self) -> str:
        return self.get_text(self.status_text).removeprefix("Status:").strip()

    def has_shortlist_action(self) -> bool:
        return any(
            element.is_displayed()
            for element in self.driver.find_elements(*self.shortlist_button)
        )

    def shortlist(self) -> None:
        self.click(self.shortlist_button)
        self.wait.until(
            expected_conditions.url_contains(
                "/recruitment/changeCandidateVacancyStatus"
            )
        )
        self.wait_until_visible(self.shortlist_heading)
        self.click(self.save_button)

        def shortlist_result(driver: WebDriver) -> tuple[str, str] | bool:
            for toast in driver.find_elements(*self.toast_content):
                if toast.is_displayed():
                    toast_text = toast.text.strip()
                    if "Successfully" in toast_text or "Success" in toast_text:
                        return "shortlisted", ""
                    return "error", toast_text
            if any(
                element.is_displayed()
                and element.text.removeprefix("Status:").strip() == "Shortlisted"
                for element in driver.find_elements(*self.status_text)
            ):
                return "shortlisted", ""
            return False

        result, message = self.wait.until(shortlist_result)
        if result == "error":
            raise RuntimeError(f"Could not shortlist candidate: {message}")
