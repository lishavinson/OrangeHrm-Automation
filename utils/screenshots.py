
import os
from datetime import datetime


def take_screenshot(driver, test_name):

    # Create screenshots folder if it doesn't exist
    screenshot_dir = "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    # Generate unique screenshot filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_name = f"{test_name}_{timestamp}.png"

    file_path = os.path.join(screenshot_dir, file_name)

    # Capture screenshot
    driver.save_screenshot(file_path)

    print(f"Screenshot saved: {file_path}")

    return file_path
