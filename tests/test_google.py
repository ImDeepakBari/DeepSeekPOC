import pytest
from selenium import webdriver
from pages.google import GooglePage
from config.settings import Config


@pytest.fixture(scope="function")
def browser():
    driver = webdriver.Safari()
    driver.implicitly_wait(Config.TIMEOUT)
    yield driver
    driver.quit()


def test_google_search(browser):
    google_page = GooglePage(browser)
    results = google_page.perform_search("Tiger")
    assert results.is_displayed()
    assert "Tiger" in browser.title
