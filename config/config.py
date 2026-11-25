import os


BASE_URL = os.getenv(
    "BASE_URL",
    "https://opensource-demo.orangehrmlive.com",
).rstrip("/")
BROWSER = os.getenv("BROWSER", "chrome").strip().lower()
TIMEOUT = int(os.getenv("TIMEOUT", "30"))
