from time import time_ns


PIM_CONFIGURATION_ITEMS = [
    "Optional Fields",
    "Custom Fields",
    "Data Import",
    "Reporting Methods",
    "Termination Reasons",
]

PIM_LOOKUP_PAGES = [
    ("Reporting Methods", "Reporting Methods"),
    ("Termination Reasons", "Termination Reasons"),
]


def create_employee_data() -> dict[str, str]:
    employee_id = str(time_ns())[-9:]
    return {
        "first_name": f"Auto{employee_id}",
        "middle_name": f"Middle{employee_id}",
        "last_name": "Employee",
        "employee_id": employee_id,
    }


def create_pim_lookup_name(page_name: str) -> str:
    token = str(time_ns())[-12:]
    return f"Automation {page_name} {token}"


def create_pim_report_name() -> str:
    token = str(time_ns())[-12:]
    return f"Automation PIM Report {token}"
