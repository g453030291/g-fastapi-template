import json
from typing import Any, Dict, Union

from openai import OpenAI, AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from loguru import logger

from app.core.config import settings


class OpenAIClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)

            cls._instance.sync_client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )

            cls._instance.async_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )
        return cls._instance

    def _prepare_args(self, prompt: str, system_prompt: str, model: str | None, temperature: float, json_mode: bool) -> \
    Dict[str, Any]:
        """Prepare API request arguments"""
        use_model = model if model else settings.OPENAI_MODEL

        # JSON mode requires "json" in prompt
        if json_mode and "json" not in system_prompt.lower():
            system_prompt = f"{system_prompt} (Please output in JSON format)"

        kwargs = {
            "model": use_model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        return kwargs

    def _parse_response(self, content: str, json_mode: bool) -> Union[str, Dict[str, Any]]:
        """Parse API response"""
        if json_mode:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logger.error(f"JSON parsing failed, returning raw string: {content}")
                return content
        return content

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    def chat_sync(
            self,
            prompt: str,
            system_prompt: str = "You are a helpful assistant.",
            model: str = None,
            temperature: float = 0.7,
            json_mode: bool = False
    ) -> Union[str, Dict[str, Any]]:

        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API Key missing")
            return {} if json_mode else "Error: No API Key"

        try:
            kwargs = self._prepare_args(prompt, system_prompt, model, temperature, json_mode)
            response = self.sync_client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            return self._parse_response(content, json_mode)

        except Exception as e:
            logger.error(f"OpenAI Sync Call Failed: {e}")
            raise e

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    async def chat_async(
            self,
            prompt: str,
            system_prompt: str = "You are a helpful assistant.",
            model: str = None,
            temperature: float = 0.7,
            json_mode: bool = False
    ) -> Union[str, Dict[str, Any]]:

        if not settings.OPENAI_API_KEY:
            return {} if json_mode else "Error: No API Key"

        try:
            kwargs = self._prepare_args(prompt, system_prompt, model, temperature, json_mode)
            response = await self.async_client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            return self._parse_response(content, json_mode)

        except Exception as e:
            logger.error(f"OpenAI Async Call Failed: {e}")
            raise e


openai_client = OpenAIClient()
