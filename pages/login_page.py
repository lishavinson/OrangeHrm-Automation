from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BasePage


class LoginPage(BasePage):
    username_input = (By.NAME, "username")
    password_input = (By.NAME, "password")
    login_button = (By.CSS_SELECTOR, "button[type='submit']")
    forgot_password_link = (By.CLASS_NAME, "orangehrm-login-forgot-header")
    invalid_credentials_message = (
        By.XPATH,
        "//*[normalize-space()='Invalid credentials']",
    )
    required_message = (By.XPATH, "//*[normalize-space()='Required']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def login(self, username: str, password: str) -> None:
        self.enter_text(self.username_input, username)
        self.enter_text(self.password_input, password)
        self.click(self.login_button)

    def login_with_enter(self, username: str, password: str) -> None:
        self.enter_text(self.username_input, username)
        self.enter_text(self.password_input, password)
        self.wait_until_visible(self.password_input).send_keys(Keys.ENTER)

    def open_forgot_password(self) -> None:
        self.click(self.forgot_password_link)

    def get_invalid_credentials_message(self) -> str:
        return self.get_text(self.invalid_credentials_message)

    def get_required_messages(self, minimum_count: int) -> list[WebElement]:
        return self.wait_for_elements(self.required_message, minimum_count)


class ResetPasswordPage(BasePage):
    reset_password_title = (
        By.XPATH,
        "//h6[normalize-space()='Reset Password']",
    )
    username_input = (By.NAME, "username")
    cancel_button = (By.CSS_SELECTOR, "button[type='button']")
    reset_password_button = (By.CSS_SELECTOR, "button[type='submit']")
    required_message = (By.XPATH, "//*[normalize-space()='Required']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def get_title(self) -> str:
        return self.get_text(self.reset_password_title)

    def enter_username(self, username: str) -> None:
        self.enter_text(self.username_input, username)

    def submit_reset_request(self) -> None:
        self.click(self.reset_password_button)

    def get_required_messages(self, minimum_count: int) -> list[WebElement]:
        return self.wait_for_elements(self.required_message, minimum_count)

    def cancel(self) -> None:
        self.click(self.cancel_button)
