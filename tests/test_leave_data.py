from datetime import date, datetime, timedelta

import test_data.leave_data as leave_data


def test_create_valid_leave_dates_looks_past_near_term_bookings(
    monkeypatch,
) -> None:
    class FixedDate(date):
        @classmethod
        def today(cls) -> date:
            return cls(2026, 1, 1)

    monkeypatch.setattr(leave_data, "date", FixedDate)
    first_date = leave_data.next_business_day()
    unavailable_dates = {
        first_date + timedelta(days=offset)
        for offset in range(21)
        if (first_date + timedelta(days=offset)).weekday() < 5
    }

    from_date, to_date = leave_data.create_valid_leave_dates(unavailable_dates)

    selected_date = datetime.strptime(from_date, "%Y-%d-%m").date()
    assert from_date == to_date
    assert selected_date.weekday() < 5
    assert selected_date not in unavailable_dates
    assert selected_date > first_date + timedelta(days=20)
