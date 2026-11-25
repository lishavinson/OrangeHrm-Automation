import os
from time import time_ns


RECRUITMENT_TEST_VACANCY = os.getenv(
    "RECRUITMENT_TEST_VACANCY",
    "Senior QA Lead",
)


def create_candidate_data() -> dict[str, str]:
    token = str(time_ns())[-12:]
    first_name = f"Automation{token}"
    last_name = "Candidate"
    return {
        "first_name": first_name,
        "last_name": last_name,
        "full_name": f"{first_name} {last_name}",
        "email": f"automation{token}@example.com",
    }


def create_unknown_candidate_name() -> str:
    return f"MissingCandidate{time_ns()}"
