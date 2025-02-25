import json
import os
from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from utils.healer_v1 import HybridLocatorHealer
from config.settings import Config


class BasePageV1:
    def __init__(self, driver):
        self.driver = driver
        self.healer = HybridLocatorHealer(
            ai_endpoint="http://localhost:1234/v1/chat/completions"
        )
        self.locator_retries = Config.LOCATOR_RETRIES
        self.timeout = Config.TIMEOUT
        self.history_file = os.path.join("locator_history", "locator_changes.json")
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

    def find_element(self, locator_dict, element_name):
        original_locator = locator_dict[element_name]
        for attempt in range(self.locator_retries + 1):
            try:
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located(original_locator))

                WebDriverWait(self.driver, 5).until(
                    EC.visibility_of(element))
                return element

            except Exception as e:
                if attempt == self.locator_retries:
                    self._log_locator_history(
                        element_name,
                        old_locator=original_locator,
                        new_locator=None,
                        success=False
                    )
                    raise

                healed = self._heal_locator(element_name)
                if healed:
                    self._log_locator_history(
                        element_name,
                        old_locator=original_locator,
                        new_locator=(healed['type'], healed['value']),
                        success=True
                    )
                    locator_dict[element_name] = (healed['type'], healed['value'])

    def _heal_locator(self, element_name):
        page_source = self.driver.page_source
        description = f"{self.__class__.__name__} {element_name}"
        return self.healer.heal_locator(page_source, description)

    def _log_locator_history(self, element_name, old_locator, new_locator, success):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "test_case": os.environ.get('PYTEST_CURRENT_TEST'),
            "element": element_name,
            "old_locator": {
                "strategy": old_locator[0],
                "value": old_locator[1]
            },
            "new_locator": {
                "strategy": new_locator[0] if new_locator else None,
                "value": new_locator[1] if new_locator else None
            },
            "success": success,
            "page_source": self._save_page_source(element_name)
        }

        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r+') as f:
                    data = json.load(f)
                    data.append(entry)
                    f.seek(0)
                    json.dump(data, f, indent=2)
            else:
                with open(self.history_file, 'w') as f:
                    json.dump([entry], f, indent=2)
        except Exception as e:
            print(f"Failed to log history: {str(e)}")

    def _save_page_source(self, element_name):
        filename = f"failed_{element_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join("failed_pages", filename)
        return filename
