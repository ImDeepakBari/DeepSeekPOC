from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from utils.healer import DeepSeekLocatorHealer
from config.settings import Config
from utils.local_healer import LocalDeepSeekHealer


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        # self.healer = DeepSeekLocatorHealer(Config.DEEPSEEK_API_KEY)
        self.healer = LocalDeepSeekHealer()
        self.timeout = Config.TIMEOUT
        self.locator_retries = Config.LOCATOR_RETRIES

    def find_element(self, locator_dict, element_name):
        locator = locator_dict[element_name]
        for attempt in range(self.locator_retries + 1):
            try:
                return WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located(locator)
                )
            except (NoSuchElementException, TimeoutException):
                if attempt == self.locator_retries:
                    raise
                new_locator = self._heal_locator(element_name)
                if new_locator:
                    locator_dict[element_name] = new_locator

    def _heal_locator(self, element_name):
        page_source = self.driver.page_source
        description = f"{self.__class__.__name__} {element_name}"
        return self.healer.heal_locator(page_source, description)
