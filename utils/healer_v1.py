from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process
from selenium.webdriver.common.by import By
import logging
import requests
import json


class HybridLocatorHealer:
    def __init__(self, ai_endpoint=None):
        self.min_fuzzy_score = 80
        self.ai_endpoint = ai_endpoint
        self.logger = logging.getLogger(__name__)

    def heal_locator(self, page_source, element_description):
        healed = self._heal_with_bs4(page_source, element_description)
        if healed:
            return healed

        if self.ai_endpoint:
            return self._heal_with_ai(page_source, element_description)

        return None

    def _heal_with_bs4(self, page_source, description):
        try:
            soup = BeautifulSoup(page_source, 'html.parser')
            strategies = []

            text_element = self._fuzzy_text_match(soup, description)
            if text_element:
                strategies.extend(self._gen_text_locators(text_element))

            attr_element = self._find_by_attributes(soup, description)
            if attr_element:
                strategies.extend(self._gen_attribute_locators(attr_element))

            return strategies[0] if strategies else None

        except Exception as e:
            self.logger.error(f"BS4 healing failed: {str(e)}")
            return None

    def _heal_with_ai(self, page_source, description):
        try:
            prompt = f"""Given this HTML fragment:
            {page_source[:3000]}
            Generate RELIABLE locators for element described as: {description}
            Requirements:
            1. Get all the identical locator similar as description
            2. Use try and catch block for checking valid locator
            3. Check for similar tag , id , name of locator
            4. Use combination of siblings, parent to find out locator
            4. Prefer visible elements

            Return JSON format:
            {{"strategies": [{{"type": "css|xpath", "value": "selector", "confidence": 0-100}}]}}"""
            response = requests.post(
                self.ai_endpoint,
                json={"model": "deepseek-r1-distill-qwen-7b", "messages": [{"role": "user", "content": prompt}]},
                timeout=25
            )

            return json.loads(response.json()['choices'][0]['message']['content'])['strategies'][0]

        except Exception as e:
            self.logger.error(f"AI healing failed: {str(e)}")
            return None

    def _fuzzy_text_match(self, soup, description):
        elements = soup.find_all(string=True)
        texts = [e.strip() for e in elements if e.strip()]

        if not texts:
            return None

        best_match, score = process.extractOne(
            description,
            texts,
            scorer=fuzz.partial_ratio
        )

        return soup.find(string=best_match).parent if score >= self.min_fuzzy_score else None

    def _find_by_attributes(self, soup, description):
        target_keywords = description.lower().split()
        for attr in ['id', 'name', 'data-testid', 'aria-label']:
            for element in soup.find_all(**{attr: True}):
                if any(kw in element[attr].lower() for kw in target_keywords):
                    return element
        return None

    def _gen_text_locators(self, element):
        text = element.get_text().strip()
        return [
            {'type': 'xpath', 'value': f'//*[contains((text()), "{text}")]'},
            {'type': 'css', 'value': f':contains("{text}")'}
        ]

    def _gen_attribute_locators(self, element):
        locators = []
        for attr in ['id', 'name', 'data-testid']:
            if attr in element.attrs:
                locators.extend([
                    {'type': 'css', 'value': f'{element.name}[{attr}="{element[attr]}"]'},
                    {'type': 'xpath', 'value': f'//{element.name}[@{attr}="{element[attr]}"]'}
                ])
        return locators