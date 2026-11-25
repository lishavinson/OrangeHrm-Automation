from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config.config import TIMEOUT


class BasePage:
    def __init__(self, driver: WebDriver, timeout: int = TIMEOUT) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_until_visible(self, locator: tuple[str, str]) -> WebElement:
        return self.wait.until(
            expected_conditions.visibility_of_element_located(locator)
        )

    def click(self, locator: tuple[str, str]) -> None:
        def click_when_available(driver: WebDriver) -> bool:
            try:
                element = driver.find_element(*locator)
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    return True
            except (
                ElementClickInterceptedException,
                StaleElementReferenceException,
            ):
                return False
            return False

        self.wait.until(click_when_available)

    def enter_text(self, locator: tuple[str, str], value: str) -> None:
        def enter_when_available(driver: WebDriver) -> bool:
            try:
                element = driver.find_element(*locator)
                if not element.is_displayed() or not element.is_enabled():
                    return False
                element.send_keys(Keys.CONTROL, "a")
                element.send_keys(Keys.BACKSPACE)
                element.send_keys(value)
                return element.get_attribute("value") == value
            except StaleElementReferenceException:
                return False

        self.wait.until(enter_when_available)

    def get_text(self, locator: tuple[str, str]) -> str:
        return self.wait_until_visible(locator).text

    def is_visible(self, locator: tuple[str, str]) -> bool:
        return self.wait.until(
            expected_conditions.visibility_of_element_located(locator)
        ).is_displayed()

    def wait_for_elements(
        self,
        locator: tuple[str, str],
        minimum_count: int,
    ) -> list[WebElement]:
        self.wait.until(
            lambda driver: len(driver.find_elements(*locator)) >= minimum_count
        )
        return self.driver.find_elements(*locator)
