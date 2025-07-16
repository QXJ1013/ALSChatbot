# app/utils/ibm_client.py
import aiohttp
import os
import structlog

logger = structlog.get_logger()

class IBMClient:
    """IBM Watson / Granite async API wrapper."""

    def __init__(self,
                 api_key: str = None,
                 base_url: str = None,
                 project_id: str = None,
                 model: str = None):
        self.api_key = api_key or os.getenv("IBM_API_KEY")
        self.base_url = base_url or os.getenv("IBM_API_URL")
        self.project_id = project_id or os.getenv("IBM_PROJECT_ID")
        self.model = model or os.getenv("IBM_MODEL_NAME", "granite-13b-chat-v2")

        if not self.api_key or not self.base_url:
            raise ValueError("IBM API credentials are missing.")

    async def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate response using IBM Watsonx LLM (Granite)."""
        url = f"{self.base_url}/v1/projects/{self.project_id}/deployments/{self.model}/predictions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "input": {
                "prompt": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.6
                }
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error("IBM LLM API error", status=resp.status, detail=error_text)
                    raise RuntimeError(f"IBM LLM API error: {resp.status}")

                data = await resp.json()
                return data.get("results", [{}])[0].get("generated_text", "No response generated.")
