from urllib.parse import urlsplit

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions

from pages.base_page import BasePage


class DashboardPage(BasePage):
    sidebar = (By.CSS_SELECTOR, "nav[aria-label='Sidepanel']")
    sidebar_module_links = (
        By.XPATH,
        "//nav[@aria-label='Sidepanel']//a[contains(@href, '/web/index.php/')]",
    )
    dashboard_heading = (By.XPATH, "//h6[normalize-space()='Dashboard']")
    profile_menu_toggle = (By.CSS_SELECTOR, "span.oxd-userdropdown-tab")
    profile_menu_items = (By.CSS_SELECTOR, "[role='menuitem']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.sidebar)
        self.wait_until_visible(self.dashboard_heading)

    def is_sidebar_visible(self) -> bool:
        return self.is_visible(self.sidebar)

    def get_sidebar_module_names(self) -> list[str]:
        links = self.wait.until(
            lambda driver: [
                link
                for link in driver.find_elements(*self.sidebar_module_links)
                if link.is_displayed()
            ]
        )
        return [link.text.strip() for link in links]

    def get_heading(self) -> str:
        return self.get_text(self.dashboard_heading)

    def open_profile_menu(self) -> None:
        self.click(self.profile_menu_toggle)
        self.wait.until(
            expected_conditions.visibility_of_element_located(
                self.profile_menu_items
            )
        )

    def get_profile_menu_items(self) -> list[str]:
        items = self.wait_for_elements(self.profile_menu_items, minimum_count=4)
        return [item.text for item in items]

    def navigate_to_module(self, module_name: str) -> str:
        module_link = (
            By.XPATH,
            f"//nav[@aria-label='Sidepanel']//a[normalize-space()='{module_name}']",
        )
        link = self.wait.until(
            expected_conditions.element_to_be_clickable(module_link)
        )
        href = link.get_attribute("href")
        href_path = urlsplit(href or "").path
        route_parts = href_path.split("/web/index.php/", maxsplit=1)
        if len(route_parts) != 2 or not route_parts[1]:
            raise ValueError(
                f"Sidebar link {module_name!r} has an unexpected href: {href!r}."
            )
        module_route = f"/{route_parts[1].split('/', maxsplit=1)[0]}/"

        link.click()
        self.wait.until(
            lambda driver: module_route in urlsplit(driver.current_url).path
        )
        return module_route
