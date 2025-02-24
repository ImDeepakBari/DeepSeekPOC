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

        prompt = f"""Analyze this page source and suggest the most reliable locator:
        Page excerpt: {page_source[:3000]}
        Element description: {element_description}
        Respond ONLY with JSON format: {{"type": "xpath|css|id", "value": "selector"}}"""

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json={
                    "model": "deepseek-coder",
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
