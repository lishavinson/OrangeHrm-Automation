import pytest

from pages.login_page import LoginPage, ResetPasswordPage
from test_data.login_data import (
    INVALID_PASSWORD,
    INVALID_USERNAME,
    VALID_PASSWORD,
    VALID_USERNAME,
)


@pytest.mark.login
@pytest.mark.smoke
@pytest.mark.parametrize(
    ("username", "password"),
    [(VALID_USERNAME, VALID_PASSWORD)],
    ids=["TC_LOGIN_001"],
)
def test_login_with_valid_credentials(driver, username, password):
    login_page = LoginPage(driver)
    login_page.login(username, password)

    assert "/dashboard/index" in driver.current_url


@pytest.mark.login
@pytest.mark.regression
@pytest.mark.parametrize(
    ("username", "password"),
    [
        (INVALID_USERNAME, VALID_PASSWORD),
        (VALID_USERNAME, INVALID_PASSWORD),
        (INVALID_USERNAME, INVALID_PASSWORD),
    ],
    ids=[
        "TC_LOGIN_002_invalid_username_valid_password",
        "TC_LOGIN_003_valid_username_invalid_password",
        "TC_LOGIN_004_invalid_username_invalid_password",
    ],
)
def test_login_rejects_invalid_credentials(driver, username, password):
    login_page = LoginPage(driver)
    login_page.login(username, password)

    assert login_page.get_invalid_credentials_message() == "Invalid credentials"


@pytest.mark.login
@pytest.mark.regression
def test_TC_LOGIN_005_username_empty(driver):
    login_page = LoginPage(driver)
    login_page.login("", VALID_PASSWORD)

    assert len(login_page.get_required_messages(minimum_count=1)) == 1


@pytest.mark.login
@pytest.mark.regression
def test_TC_LOGIN_006_password_empty(driver):
    login_page = LoginPage(driver)
    login_page.login(VALID_USERNAME, "")

    assert len(login_page.get_required_messages(minimum_count=1)) == 1


@pytest.mark.login
@pytest.mark.regression
def test_TC_LOGIN_007_both_credentials_empty(driver):
    login_page = LoginPage(driver)
    login_page.login("", "")

    assert len(login_page.get_required_messages(minimum_count=2)) == 2


@pytest.mark.login
@pytest.mark.regression
def test_TC_LOGIN_009_submit_with_enter(driver):
    login_page = LoginPage(driver)
    login_page.login_with_enter(VALID_USERNAME, VALID_PASSWORD)

    assert "/dashboard/index" in driver.current_url


@pytest.mark.login
@pytest.mark.regression
def test_forgot_password_opens_reset_page(driver):
    login_page = LoginPage(driver)
    login_page.open_forgot_password()
    reset_password_page = ResetPasswordPage(driver)

    assert reset_password_page.get_title() == "Reset Password"


@pytest.mark.login
@pytest.mark.regression
def test_forgot_password_requires_username(driver):
    login_page = LoginPage(driver)
    login_page.open_forgot_password()
    reset_password_page = ResetPasswordPage(driver)
    reset_password_page.submit_reset_request()

    assert len(reset_password_page.get_required_messages(minimum_count=1)) == 1


@pytest.mark.login
@pytest.mark.regression
def test_forgot_password_cancel_returns_to_login(driver):
    login_page = LoginPage(driver)
    login_page.open_forgot_password()
    reset_password_page = ResetPasswordPage(driver)
    reset_password_page.cancel()

    assert "/auth/login" in driver.current_url
