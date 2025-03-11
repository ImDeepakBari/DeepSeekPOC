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

    def _select_best_strategy(self, strategies):
        if not strategies:
            return None

        valid_strategies = [s for s in strategies if self._validate_in_dom(s)]
        return self._select_best_strategy(valid_strategies)

        priority_order = [
            'exact_match',
            'number_variation',
            'common_suffix',
            'common_prefix',
            'typo_fix'
        ]

        return sorted(
            strategies,
            key=lambda x: (
                -priority_order.index(x['reason']),
                -x['confidence']
            )
        )[0]

    def _heal_with_ai(self, page_source, description):

        try:

            prompt = f"""Analyze this HTML fragment and suggest locator fixes:
            {page_source[:3000]}

            Original locator problem: {description}

            Requirements:
            1. Identify attribute values that are close matches to the original
            2. Check for these patterns in order:
               - Exact substring matches (e.g., "username" in "username12")
               - Common suffixes/prefixes (e.g., "_username", "username_input")
               - Number variations (e.g., "username1", "username2")
               - Typos (e.g., "usernmae", "user_name")
            3. For name/id/class attributes:
               a. Generate 3 variations of the original value
               b. Check existence in DOM
               c. Prioritize visible elements
            4. Return only existing locators from the DOM

            Example: If original is 'username12', suggest:
            - name="username" (exact match)
            - name="username1" (number variation)
            - name="username_field" (common suffix)

            Return JSON format:
            {{
                "strategies": [
                    {{
                        "type": "name|xpath|css",
                        "value": "selector",
                        "confidence": 1-100,
                        "reason": "match_type"
                    }}
                ]
            }}"""


            response = requests.post(
                self.ai_endpoint,
                json={
                    "model": "deepseek-coder",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                },
                timeout=550)

            strategies = json.loads(response.json()['choices'][0]['message']['content'])['strategies']
            return self._select_best_strategy(strategies)
        except Exception as e:
            pass

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