import pytest
from selenium import webdriver
from pages.bank import BankPage


def test_search():
    driver = webdriver.Safari()
    driver.maximize_window()
    driver.get("https://www.google.com")

    try:
        page = BankPage(driver)
        page.perform_login_action("DeepakBari", "@lteryX9000")
        print('Tc successfully passed')

    finally:
        def pytest_sessionfinish():
            from utils.history import LocatorHistoryAnalyzer
            analyzer = LocatorHistoryAnalyzer("locator_history/locator_changes.json")
            flaky = analyzer.get_flaky_locators()
            print(f"Flaky locators: {flaky}")

        pytest_sessionfinish()
        driver.quit()
        print('driver is closed')