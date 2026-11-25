from time import time_ns


ROLE_OPTIONS = ["-- Select --", "Admin", "ESS"]
STATUS_OPTIONS = ["-- Select --", "Enabled", "Disabled"]
ADMIN_ROLE = "Admin"
ENABLED_STATUS = "Enabled"
NO_MATCH_USERNAME = "NoSuchAdminUser987"

ADMIN_SUBCATEGORIES = [
    ("User Management", "Users", "System Users"),
    ("Organization", "General Information", "General Information"),
    ("Organization", "Locations", "Locations"),
    ("Organization", "Structure", "Organization Structure"),
    ("Qualifications", "Skills", "Skills"),
    ("Qualifications", "Education", "Education"),
    ("Qualifications", "Licenses", "Licenses"),
    ("Qualifications", "Languages", "Languages"),
    ("Qualifications", "Memberships", "Memberships"),
    ("More", "Nationalities", "Nationalities"),
    ("More", "Corporate Branding", "Corporate Branding"),
]

ADMIN_REQUIRED_FORM_PAGES = [
    ("Organization", "Locations", "Locations", 2),
    ("Qualifications", "Skills", "Skills", 1),
    ("Qualifications", "Education", "Education", 1),
    ("Qualifications", "Licenses", "Licenses", 1),
    ("Qualifications", "Languages", "Languages", 1),
    ("Qualifications", "Memberships", "Memberships", 1),
    ("More", "Nationalities", "Nationalities", 1),
]


def create_admin_subcategory_data(item: str) -> dict[str, str]:
    token = str(time_ns())[-12:]

    if item == "Education":
        return {"Level": f"Automation Education {token}"}

    fields = {"Name": f"Automation {item} {token}"}

    if item == "Locations":
        fields.update(
            {
                "City": f"Test City {token}",
                "State/Province": "Ontario",
                "Zip/Postal Code": "A1B 2C3",
                "Country": "Canada",
                "Address": f"Admin test address {token}",
                "Notes": f"Admin test notes {token}",
            }
        )
    elif item == "Skills":
        fields["Description"] = f"Automation skill details {token}"

    return fields


GENERAL_INFORMATION_FIELDS = [
    "Organization Name",
    "Number of Employees",
    "Registration Number",
    "Tax ID",
    "Phone",
    "Fax",
    "Email",
    "Address Street 1",
    "Address Street 2",
    "City",
    "State/Province",
    "Zip/Postal Code",
    "Country",
    "Notes",
]

CORPORATE_BRANDING_FIELDS = [
    "Primary Color",
    "Secondary Color",
    "Primary Font Color",
    "Secondary Font Color",
    "Primary Gradient Color 1",
    "Primary Gradient Color 2",
    "Client Logo",
    "Client Banner",
    "Login Banner",
]
