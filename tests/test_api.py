import os
import requests
from dotenv import load_dotenv

load_dotenv()


def test_api_connection():
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-coder",
            "messages": [{"role": "user", "content": "Test connection"}]
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")


test_api_connection()


def test_local_api_healing_config():
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        json={
            "model": "deepseek-r1-distill-qwen-7b",
            "messages": [{
                "role": "user",
                "content": "Create xpath for search input in Google's HTML"
            }],
            "temperature": 0.3
        }
    )

    print("Response Status:", response.status_code)
    print("Generated Content:", response.json()['choices'][0]['message']['content'])



