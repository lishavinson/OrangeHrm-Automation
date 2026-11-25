from collections.abc import Iterator

import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config.config import BASE_URL, TIMEOUT
from pages.add_candidate_page import AddCandidatePage
from pages.candidate_profile_page import CandidateProfilePage
from pages.login_page import LoginPage
from pages.recruitment_page import RecruitmentPage
from test_data.login_data import VALID_PASSWORD, VALID_USERNAME
from test_data.recruitment_data import (
    RECRUITMENT_TEST_VACANCY,
    create_candidate_data,
    create_unknown_candidate_name,
)


@pytest.fixture
def recruitment_page(driver: WebDriver) -> RecruitmentPage:
    LoginPage(driver).login(VALID_USERNAME, VALID_PASSWORD)
    WebDriverWait(driver, TIMEOUT).until(
        expected_conditions.url_contains("/dashboard/index")
    )
    driver.get(f"{BASE_URL}/web/index.php/recruitment/viewCandidates")

    page = RecruitmentPage(driver)
    page.wait_until_loaded()
    return page


def open_add_candidate(recruitment_page: RecruitmentPage) -> AddCandidatePage:
    recruitment_page.open_add_candidate()
    page = AddCandidatePage(recruitment_page.driver)
    page.wait_until_loaded()
    return page


def candidate_name_in_rows(candidate_name: str, rows: list[str]) -> bool:
    expected_name = " ".join(candidate_name.split())
    return any(expected_name in " ".join(row.split()) for row in rows)


def create_candidate(
    recruitment_page: RecruitmentPage,
    candidate: dict[str, str],
) -> None:
    add_candidate_page = open_add_candidate(recruitment_page)
    add_candidate_page.set_first_name(candidate["first_name"])
    add_candidate_page.set_last_name(candidate["last_name"])
    add_candidate_page.set_email(candidate["email"])
    candidate["vacancy_selected"] = (
        add_candidate_page.select_vacancy(RECRUITMENT_TEST_VACANCY) or ""
    )
    add_candidate_page.set_consent_to_keep_data(True)
    add_candidate_page.save()
    add_candidate_page.wait_until_saved()
    recruitment_page.driver.get(
        f"{BASE_URL}/web/index.php/recruitment/viewCandidates"
    )
    recruitment_page.wait_until_loaded()


@pytest.fixture
def candidate_record(
    recruitment_page: RecruitmentPage,
) -> Iterator[tuple[RecruitmentPage, dict[str, str]]]:
    candidate = create_candidate_data()
    created = False
    try:
        create_candidate(recruitment_page, candidate)
        created = True
        yield recruitment_page, candidate
    finally:
        if created and candidate.get("deleted") != "true":
            recruitment_page.driver.get(
                f"{BASE_URL}/web/index.php/recruitment/viewCandidates"
            )
            recruitment_page.wait_until_loaded()
            recruitment_page.search_candidate_by_name(candidate["full_name"])
            recruitment_page.delete_candidate(candidate["full_name"])


@pytest.mark.recruitment
@pytest.mark.smoke
def test_candidate_list_is_displayed(recruitment_page: RecruitmentPage) -> None:
    assert recruitment_page.get_heading() == "Candidates"
    assert recruitment_page.is_add_candidate_button_visible()


@pytest.mark.recruitment
@pytest.mark.regression
def test_candidate_filters_can_be_reset(
    recruitment_page: RecruitmentPage,
) -> None:
    recruitment_page.set_keywords("automation")

    assert recruitment_page.get_keywords() == "automation"

    recruitment_page.reset_filters()

    assert recruitment_page.get_keywords() == ""


@pytest.mark.recruitment
@pytest.mark.regression
def test_search_with_unknown_candidate_shows_validation(
    recruitment_page: RecruitmentPage,
) -> None:
    recruitment_page.set_candidate_name(create_unknown_candidate_name())
    recruitment_page.search_candidates()

    assert recruitment_page.get_candidate_name_validation_error() == "Invalid"


@pytest.mark.recruitment
@pytest.mark.smoke
def test_add_candidate_form_is_displayed(
    recruitment_page: RecruitmentPage,
) -> None:
    add_candidate_page = open_add_candidate(recruitment_page)

    assert add_candidate_page.get_heading() == "Add Candidate"


@pytest.mark.recruitment
@pytest.mark.regression
def test_add_candidate_requires_first_name_last_name_and_email(
    recruitment_page: RecruitmentPage,
) -> None:
    add_candidate_page = open_add_candidate(recruitment_page)
    add_candidate_page.save()

    assert add_candidate_page.get_validation_errors().count("Required") == 3


@pytest.mark.recruitment
@pytest.mark.regression
def test_add_candidate_rejects_invalid_email(
    recruitment_page: RecruitmentPage,
) -> None:
    add_candidate_page = open_add_candidate(recruitment_page)
    add_candidate_page.set_first_name("Automation")
    add_candidate_page.set_last_name("Candidate")
    add_candidate_page.set_email("invalid-email")
    add_candidate_page.save()

    assert "Expected format: admin@example.com" in (
        add_candidate_page.get_validation_errors()
    )


@pytest.mark.recruitment
@pytest.mark.smoke
def test_add_candidate_with_valid_information(
    candidate_record: tuple[RecruitmentPage, dict[str, str]],
) -> None:
    recruitment_page, candidate = candidate_record
    rows = recruitment_page.search_candidate_by_name(candidate["full_name"])

    assert candidate_name_in_rows(candidate["full_name"], rows)


@pytest.mark.recruitment
@pytest.mark.regression
def test_search_candidate_by_name(
    candidate_record: tuple[RecruitmentPage, dict[str, str]],
) -> None:
    recruitment_page, candidate = candidate_record
    recruitment_page.reset_filters()
    rows = recruitment_page.search_candidate_by_name(candidate["full_name"])

    assert candidate_name_in_rows(candidate["full_name"], rows)


@pytest.mark.recruitment
@pytest.mark.regression
def test_edit_candidate_information(
    candidate_record: tuple[RecruitmentPage, dict[str, str]],
) -> None:
    recruitment_page, candidate = candidate_record
    recruitment_page.search_candidate_by_name(candidate["full_name"])
    recruitment_page.open_candidate_profile(candidate["full_name"])
    profile_page = CandidateProfilePage(recruitment_page.driver)
    profile_page.wait_until_loaded()
    profile_page.enable_editing()

    updated_first_name = f"{candidate['first_name']}Updated"
    profile_page.update_first_name(updated_first_name)
    profile_page.save()

    assert profile_page.get_first_name() == updated_first_name
    candidate["first_name"] = updated_first_name
    candidate["full_name"] = f"{updated_first_name} {candidate['last_name']}"


@pytest.mark.recruitment
@pytest.mark.regression
def test_change_candidate_status_to_shortlisted(
    candidate_record: tuple[RecruitmentPage, dict[str, str]],
) -> None:
    recruitment_page, candidate = candidate_record
    if not candidate["vacancy_selected"]:
        pytest.skip(
            "The demo has no active vacancies, so this candidate cannot be shortlisted."
        )
    recruitment_page.search_candidate_by_name(candidate["full_name"])
    recruitment_page.open_candidate_profile(candidate["full_name"])
    profile_page = CandidateProfilePage(recruitment_page.driver)
    profile_page.wait_until_loaded()
    if not profile_page.has_shortlist_action():
        pytest.skip(
            "The selected demo vacancy does not offer a shortlist action."
        )
    profile_page.shortlist()

    assert profile_page.get_status() == "Shortlisted"


@pytest.mark.recruitment
@pytest.mark.regression
def test_delete_candidate(
    candidate_record: tuple[RecruitmentPage, dict[str, str]],
) -> None:
    recruitment_page, candidate = candidate_record
    recruitment_page.search_candidate_by_name(candidate["full_name"])
    recruitment_page.delete_candidate(candidate["full_name"])
    candidate["deleted"] = "true"

    assert not any(
        " ".join(candidate["full_name"].split()) in " ".join(row.split())
        for row in recruitment_page.get_candidate_rows()
    )
