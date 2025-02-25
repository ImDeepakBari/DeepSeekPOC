from selenium.webdriver.common.by import By

from config.settings import Config
from pages.base_page_v1 import BasePageV1


class BankPage(BasePageV1):
    LOCATORS = {
        "username": (By.NAME, "username12"),
        "password": (By.NAME, "password"),
        "login_btn": (By.XPATH, "//input[@value='Log In']")
    }

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get(Config.BANK_URL)

    def perform_login_action(self, username, password):
        self.find_element(self.LOCATORS, "username").send_keys(username)
        self.find_element(self.LOCATORS, "password").send_keys(password)
        self.find_element(self.LOCATORS, "login_btn").click()
