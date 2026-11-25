from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class BuzzPage(BasePage):
    buzz_heading = (By.XPATH, "//h6[normalize-space()='Buzz']")
    post_textarea = (
        By.CSS_SELECTOR,
        "textarea[placeholder=\"What's on your mind?\"]",
    )
    post_button = (
        By.XPATH,
        "//button[@type='submit' and normalize-space()='Post']",
    )
    active_feed_filter = (
        By.CSS_SELECTOR,
        "button.orangehrm-post-filters-button.oxd-button--label-warn",
    )
    share_photos_button = (
        By.XPATH,
        "//button[@type='button' and normalize-space()='Share Photos']",
    )
    share_video_button = (
        By.XPATH,
        "//button[@type='button' and normalize-space()='Share Video']",
    )

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def wait_until_loaded(self) -> None:
        self.wait_until_visible(self.buzz_heading)

    def set_post_text(self, text: str) -> None:
        field = self.wait_until_visible(self.post_textarea)
        field.click()
        if field.get_attribute("value"):
            field.send_keys(Keys.CONTROL, "a")
        field.send_keys(text)
        self.wait.until(
            lambda driver: driver.find_element(
                *self.post_textarea
            ).get_attribute("value")
            == text
        )

    def get_post_text(self) -> str:
        return (
            self.wait_until_visible(self.post_textarea).get_attribute("value")
            or ""
        )

    def submit_post(self) -> None:
        self.click(self.post_button)

    def get_active_feed_filter(self) -> str:
        return self.get_text(self.active_feed_filter)

    def select_feed_filter(self, filter_name: str) -> None:
        self.click(
            (
                By.XPATH,
                f"//button[@type='button' and "
                f"normalize-space()='{filter_name}']",
            )
        )

    def open_share_photos(self) -> None:
        self.click(self.share_photos_button)

    def open_share_video(self) -> None:
        self.click(self.share_video_button)
