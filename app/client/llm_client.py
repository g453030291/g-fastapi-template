import json
from typing import Any, Dict, Union

from loguru import logger
from tenacity import retry, stop_after_attempt, wait_random_exponential

from app.core.config import settings


class LLMClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._init()
            cls._instance = instance
        return cls._instance

    def _init(self):
        base_url = settings.LLM_BASE_URL or None
        if settings.LLM_PROVIDER == "anthropic":
            import anthropic
            self._sync = anthropic.Anthropic(api_key=settings.LLM_API_KEY, base_url=base_url)
            self._async = anthropic.AsyncAnthropic(api_key=settings.LLM_API_KEY, base_url=base_url)
        else:
            from openai import OpenAI, AsyncOpenAI
            self._sync = OpenAI(api_key=settings.LLM_API_KEY, base_url=base_url)
            self._async = AsyncOpenAI(api_key=settings.LLM_API_KEY, base_url=base_url)

    def _prepare(self, system_prompt: str, model: str | None, json_mode: bool) -> tuple[str, str]:
        use_model = model or settings.LLM_MODEL
        sys_prompt = system_prompt
        if json_mode and "json" not in sys_prompt.lower():
            sys_prompt += " Respond in JSON format."
        return use_model, sys_prompt

    def _anthropic_kwargs(self, prompt: str, sys_prompt: str, model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        return {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": sys_prompt,
            "messages": [{"role": "user", "content": prompt}],
        }

    def _openai_kwargs(self, prompt: str, sys_prompt: str, model: str, temperature: float, json_mode: bool) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "model": model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt},
            ],
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        return kwargs

    def _parse(self, content: str, json_mode: bool) -> Union[str, Dict[str, Any]]:
        if json_mode:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logger.error(f"JSON parse failed: {content}")
                return content
        return content

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    def chat_sync(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        model: str | None = None,
        temperature: float = 0.7,
        json_mode: bool = False,
        max_tokens: int = 4096,
    ) -> Union[str, Dict[str, Any]]:
        if not settings.LLM_API_KEY:
            logger.warning("LLM API Key missing")
            return {} if json_mode else "Error: No API Key"

        use_model, sys_prompt = self._prepare(system_prompt, model, json_mode)
        try:
            if settings.LLM_PROVIDER == "anthropic":
                resp = self._sync.messages.create(**self._anthropic_kwargs(prompt, sys_prompt, use_model, temperature, max_tokens))
                content = resp.content[0].text
            else:
                resp = self._sync.chat.completions.create(**self._openai_kwargs(prompt, sys_prompt, use_model, temperature, json_mode))
                content = resp.choices[0].message.content
            return self._parse(content, json_mode)
        except Exception as e:
            logger.error(f"LLM sync call failed: {e}")
            raise

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    async def chat_async(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        model: str | None = None,
        temperature: float = 0.7,
        json_mode: bool = False,
        max_tokens: int = 4096,
    ) -> Union[str, Dict[str, Any]]:
        if not settings.LLM_API_KEY:
            return {} if json_mode else "Error: No API Key"

        use_model, sys_prompt = self._prepare(system_prompt, model, json_mode)
        try:
            if settings.LLM_PROVIDER == "anthropic":
                resp = await self._async.messages.create(**self._anthropic_kwargs(prompt, sys_prompt, use_model, temperature, max_tokens))
                content = resp.content[0].text
            else:
                resp = await self._async.chat.completions.create(**self._openai_kwargs(prompt, sys_prompt, use_model, temperature, json_mode))
                content = resp.choices[0].message.content
            return self._parse(content, json_mode)
        except Exception as e:
            logger.error(f"LLM async call failed: {e}")
            raise


llm_client = LLMClient()
