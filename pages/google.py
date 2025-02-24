from selenium.webdriver.common.by import By

from config.settings import Config
from pages.base_page import BasePage


class GooglePage(BasePage):
    LOCATORS = {
        "search_box": (By.NAME, "q"),
        "search_button": (By.XPATH, "(//input[@name='btnK'])[2]"),
        "results": (By.XPATH, "//div[@id='search']")
    }

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get(Config.BASE_URL)

    def perform_search(self, text):
        self.find_element(self.LOCATORS, "search_box").send_keys(text)
        self.find_element(self.LOCATORS, "search_button").click()
        return self.find_element(self.LOCATORS, "results")
