import os
from datetime import date, timedelta
from time import time_ns

from test_data.login_data import VALID_PASSWORD, VALID_USERNAME

LEAVE_TEST_USERNAME = os.getenv(
    "LEAVE_TEST_USERNAME",
    VALID_USERNAME,
).strip()
LEAVE_TEST_PASSWORD = os.getenv("LEAVE_TEST_PASSWORD", VALID_PASSWORD)
LEAVE_TEST_EMPLOYEE_NAME = os.getenv("LEAVE_TEST_EMPLOYEE_NAME", "").strip()
LEAVE_TEST_TYPE = os.getenv("LEAVE_TEST_TYPE", "US - Vacation")
LEAVE_TEST_BALANCE = int(os.getenv("LEAVE_TEST_BALANCE", "20"))


def next_business_day(from_date: date | None = None) -> date:
    leave_date = from_date or date.today()
    leave_date += timedelta(days=1)
    while leave_date.weekday() >= 5:
        leave_date += timedelta(days=1)
    return leave_date


def format_leave_date(leave_date: date) -> str:
    return leave_date.strftime("%Y-%d-%m")


def create_leave_comment() -> str:
    return f"Automation leave {time_ns()}"


def create_valid_leave_dates(
    unavailable_dates: set[date] | None = None,
) -> tuple[str, str]:
    unavailable_dates = unavailable_dates or set()
    first_date = next_business_day()
    candidate = first_date
    final_date = date(first_date.year, 12, 31)
    while candidate <= final_date:
        if candidate.weekday() < 5 and candidate not in unavailable_dates:
            return format_leave_date(candidate), format_leave_date(candidate)
        candidate += timedelta(days=1)
    raise ValueError("No future business day remains in the current leave period.")


def create_excess_leave_dates(
    unavailable_dates: set[date] | None = None,
) -> tuple[str, str]:
    unavailable_dates = unavailable_dates or set()
    start_date = next_business_day()
    last_date = date(start_date.year, 12, 31)
    while start_date <= last_date:
        if start_date.weekday() < 5:
            end_date = start_date
            business_days = 1
            while business_days <= LEAVE_TEST_BALANCE + 2:
                end_date += timedelta(days=1)
                if end_date.weekday() < 5:
                    business_days += 1
            if end_date.year == start_date.year and not any(
                start_date <= unavailable_date <= end_date
                for unavailable_date in unavailable_dates
            ):
                return format_leave_date(start_date), format_leave_date(end_date)
        start_date += timedelta(days=1)
    raise ValueError(
        "No non-overlapping date range remains in the current leave period "
        "to test a request exceeding the configured entitlement."
    )
