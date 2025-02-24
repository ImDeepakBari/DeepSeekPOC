# utils/healer.py
import requests
import json
import logging


class LocalDeepSeekHealer:
    def __init__(self):
        self.api_url = "http://localhost:1234/v1/chat/completions"
        self.logger = logging.getLogger(__name__)

    def heal_locator(self, page_source, element_description):
        prompt = f"""Analyze this HTML and suggest stable locators:

        Page excerpt: {page_source[:3000]}
        Element description: {element_description}

        Return ONLY JSON format:
        {{
            "strategies": [
                {{"type": "xpath", "value": "..."}},
                {{"type": "css", "value": "..."}}
            ]
        }}"""

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": "deepseek-r1-distill-qwen-7b", 
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 200
                },
                timeout=15
            )
            return self._parse_response(response.json())
        except Exception as e:
            self.logger.error(f"Healing failed: {str(e)}")
            return None

    def _parse_response(self, response):
        try:
            content = response['choices'][0]['message']['content']
            return json.loads(content)['strategies']
        except (KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"Parse error: {str(e)}")
            return None