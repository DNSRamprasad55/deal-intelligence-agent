from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings
from app.core.logging import logger


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        pass


class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL or "gemini-2.5-flash"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            logger.warning("LLM_API_KEY not configured for GeminiLLMProvider.")
            return "LLM integration is not configured."

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Instruction: {system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json={"contents": contents})
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                logger.error(f"Gemini API returned status {res.status_code}: {res.text}")
                return "Error generating response from LLM."
        except Exception as e:
            logger.error(f"Exception during Gemini API call: {str(e)}")
            return "Exception occurred while communicating with LLM."


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL or "gpt-4o-mini"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            logger.warning("LLM_API_KEY not configured for OpenAILLMProvider.")
            return "LLM integration is not configured."

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    url,
                    json={"model": self.model, "messages": messages},
                    headers=headers
                )
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "")
                return "Error generating response from OpenAI."
        except Exception as e:
            logger.error(f"OpenAI API exception: {str(e)}")
            return "Exception occurred while communicating with OpenAI."


def get_llm_provider() -> LLMProvider:
    provider_name = (settings.LLM_PROVIDER or "gemini").lower()
    if provider_name == "openai":
        return OpenAILLMProvider()
    return GeminiLLMProvider()
