import pytest
from selenium import webdriver
from pages.bank import BankPage
from config.settings import Config


@pytest.fixture(scope="function")
def browser():
    driver = webdriver.Safari()
    driver.implicitly_wait(Config.TIMEOUT)
    yield driver
    driver.quit()


def test_google_search(browser):
    bank = BankPage(browser)
    results = bank.perform_login_action("DeepakBari", "@lteryX9000")
    import time
    time.sleep(5)


