import os
import aiohttp
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
load_dotenv(os.path.join(BASE_DIR, ".env"))
print(os.getenv("HF_API_TOKEN"))
class ChatEngineLight:
    def __init__(self):
        self.api_key = os.getenv("HF_API_TOKEN")
        if not self.api_key:
            raise ValueError("HF_API_TOKEN not set!")
        self.model = os.getenv("HF_MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.2")

    async def get_response(self, message: str) -> str:
        prompt = f"You are a helpful assistant. User: {message}\nAssistant:"
        url = f"https://api-inference.huggingface.co/models/{self.model}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {"inputs": prompt}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HF API Error: {resp.status}, {await resp.text()}")
                data = await resp.json()
                return data[0]["generated_text"].replace(prompt, "").strip()
