# Project Context: OrangeHRM Test Automation

## Goal
Automate all features of the OrangeHRM demo site using Python, Selenium and PyTest, with the Page Object Model (POM) structure.

## About me
- Manual software tester, beginner in Python and Selenium
- Explain code simply, step by step, and say what each change does
- Work in small steps: one module or one page at a time
- Show the full file whenever code changes

## Application under test
- URL: https://opensource-demo.orangehrmlive.com/
- Username: Admin
- Password: admin123
- It is a public demo site. Data is shared and resets from time to time, so never depend on existing records. Use unique data (for example a timestamp in names) for anything I create, and clean it up when possible.

## Leave test account
Leave tests change employee entitlements and submit leave requests. By default, they use the public demo credentials and discover the logged-in employee name. The demo is shared and may change or have overlapping requests, so test results can vary. To use a separate account, configure these environment variables before running Leave tests:

```powershell
$env:BASE_URL = "https://your-isolated-orangehrm-instance"
$env:LEAVE_TEST_USERNAME = "your-test-username"
$env:LEAVE_TEST_PASSWORD = "your-test-password"
$env:LEAVE_TEST_EMPLOYEE_NAME = "Your Test Employee"
$env:LEAVE_TEST_TYPE = "US - Vacation"
$env:LEAVE_TEST_BALANCE = "20"
python -m pytest -m leave
```

The employee must be associated with the configured account and have the selected leave type available. `LEAVE_TEST_USERNAME`, `LEAVE_TEST_PASSWORD`, and `LEAVE_TEST_EMPLOYEE_NAME` are optional and default to the demo credentials and automatic employee-name discovery. If the demo contains multiple employees with that name, set `LEAVE_TEST_EMPLOYEE_NAME` to a name that uniquely identifies the intended employee; otherwise, use an isolated test account. `LEAVE_TEST_TYPE` and `LEAVE_TEST_BALANCE` default to `US - Vacation` and `20`. Keep account credentials in environment variables rather than source control, and do not run the Leave tests concurrently against the same account. The excess-balance case is skipped if the current leave period has too few days remaining for a valid test range.

## Tech stack
- Python 3, Selenium WebDriver, PyTest
- pytest-html for reports
- Editor: VS Code
- Browsers: Chrome and Firefox (selected from `BROWSER` in config)

## Locator rules (very important)
1. Use ONLY live locators: locators taken from the real, running site. Never guess or invent a locator.
2. If you cannot see the real HTML of an element, ask me to paste it (from browser DevTools, Inspect, Copy outerHTML). Do not continue with a made-up locator.
3. Preferred order: `id`, `name`, other stable attributes (`placeholder`, `type`, `aria-label`), then relative XPath based on visible label text.
4. Avoid absolute XPath, index-based XPath (`[1]`, `[2]`), long CSS class chains, and auto-generated attributes (for example `data-v-xxxx`).
5. Every locator must be checked against the live page before use. I will confirm it works.
6. All locators live in page classes only. No locators in test files.

## Framework rules
- Page Object Model: one page class per page or section, inside `pages/`
- A base page class holds the common actions (click, type, wait, get text)
- Assertions stay in the test files, not in page classes
- Explicit waits only (`WebDriverWait` with `expected_conditions`). No `time.sleep()`
- Test data is separate from tests, inside `test_data/`
- Config values (`BASE_URL`, `BROWSER`, `TIMEOUT`) live in `config/config.py`
- Do not modify existing files unless I ask. Do not add packages without telling me why

## Folder structure
```
orangehrm-automation/
├── config/
│   └── config.py
├── pages/
├── tests/
├── test_data/
├── utils/
├── reports/
├── screenshots/
├── logs/
├── conftest.py
├── pytest.ini
└── requirements.txt
```

## Modules to automate
Check this list against the live left-side menu and correct it if needed.

1. Login / Logout (valid, invalid, empty fields, forgot password)
2. Admin (user management, job titles, pay grades, organization, and so on)
3. PIM (add, search, edit, delete employees; employee details)
4. Leave (apply, assign, leave list, entitlements, leave types)
5. Time (timesheets, attendance, project info)
6. Recruitment (candidates, vacancies)
7. My Info (personal details, contact details, and other tabs)
8. Performance
9. Directory
10. Claim
11. Buzz
12. Maintenance
13. Dashboard (widgets and quick launch)

## How we work on each module
1. List the features and test scenarios of the module (positive and negative)
2. I inspect the live page and share the HTML of the elements
3. You write the locators and the page object from that HTML only
4. You write the tests using that page object
5. I run them, share any errors, and we fix them before the next module

## Test markers
`smoke`, `regression`, plus one marker per module (for example `login`, `admin`, `pim`, `leave`).

## Current status
- The project folder structure and initial login automation have been created.
- Login tests cover valid credentials, invalid credentials, missing username, missing password, both fields empty, and the Forgot Password page.
- Admin tests cover User Management search filters, action-button visibility, reset behavior, and Add User required-field validation. Organization General Information edit mode and fields, required-field validation on Locations and each Qualifications/Nationalities add form, and unique-record create/edit/delete workflows with saved-field verification on those same forms are also covered. The current Organization Structure state and Corporate Branding fields/Preview are checked; the public demo currently shows no editable hierarchy, and data-changing organization settings and branding are not published by tests.
- Dashboard tests cover the dashboard heading and visible sidebar, the user profile menu options, and navigation to each visible sidebar module.
- Performance tests cover module navigation and KPI form validation, creation, search/reset, editing, and deletion. When the live KPI form has no selectable job title, CRUD fixtures create a unique temporary title and remove it during cleanup.
- PIM tests cover the employee list, adding an employee, searching by employee ID, editing an employee's first name, deleting an employee, and searching for an unknown employee ID. CRUD tests create unique employee IDs and remove their test employees during fixture cleanup.
- Recruitment tests cover candidate creation and search, editing candidate details, shortlisting a candidate, deleting candidates, filter reset, unknown candidate-name validation, required-field validation, and invalid email validation. CRUD scenarios use unique candidate data and remove created records during fixture cleanup.
- Leave tests cover Apply Leave validation and submission, My Leave and Leave List rendering, Leave List search/reset, Assign Leave required-field validation, and navigation to Leave List, Assign Leave, reports, Configure, and Entitlements. Tests that submit leave applications or change entitlements use the shared demo account and should not run concurrently.
- Time tests cover Timesheets, Attendance, Reports, and Project Info dropdown navigation; employee-name timesheet lookup; and safe validation of timesheet, report, customer, and project forms. Tests do not punch in/out or save timesheets, reports, customers, or projects.
- Install dependencies with `python -m pip install -r requirements.txt`, then run the suite with `python -m pytest`.
- Every test run creates or replaces `reports/test-report.html`, a self-contained HTML report with each testcase's result, duration, and failure details. Open this file in a browser to review the run.
- When a testcase fails during its execution phase and has the `driver` fixture, its browser screenshot is saved in `screenshots/` and embedded in the HTML report. The screenshot filename is based on the testcase ID; rerunning the same testcase replaces its previous screenshot.
- Continue using the live-page HTML workflow before adding locators for other modules.
