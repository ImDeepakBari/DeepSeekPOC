import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEEPSEEK_API_KEY = os.getenv("sk-2d840c1ac4b04276928143fad15c743e")
    BASE_URL = "https://www.google.com"
    BANK_URL = "https://parabank.parasoft.com/parabank/index.htm"
    BROWSER = "Safari"
    HEADLESS = False
    TIMEOUT = 10
    LOCATOR_RETRIES = 2
    MODEL = "gpt-3.5-turbo"
