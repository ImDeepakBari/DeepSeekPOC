import requests
import json
import logging


class DeepSeekLocatorHealer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        # self.api_url = "https://api.openai.com/v1/chat/completions"
        self.logger = logging.getLogger(__name__)

    def heal_locator(self, page_source, element_description):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        prompt = f"""Given this HTML fragment:
                    {page_source[:3000]}
                    Generate RELIABLE locators for element described as: {element_description}
                    Requirements:
                    1. Prefer CSS over XPath
                    2. Must be unique
                    3. Avoid index-based selectors
                    4. Prefer visible elements

                    Return JSON format:
                    {{"strategies": [{{"type": "css|xpath", "value": "selector", "confidence": 0-100}}]}}"""

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json={
                    "model": "deepseek-r1-distill-qwen-7b",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                },
                timeout=10
            )
            response.raise_for_status()
            return self._parse_response(response.json())
        except Exception as e:
            self.logger.error(f"Healer error: {str(e)}")
            return None

    def _parse_response(self, response):
        try:
            content = response['choices'][0]['message']['content']
            return content['type'], content['value']
        except (KeyError, json.JSONDecodeError):
            return None
