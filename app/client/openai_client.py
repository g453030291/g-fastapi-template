from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from loguru import logger
from app.core.config import settings

class OpenAIClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)
            cls._instance.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )
        return cls._instance

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    async def chat_completion(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        """
        简单的对话封装，带自动重试机制
        """
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API Key not configured")
            return "Error: API Key not configured"

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            raise e

openai_client = OpenAIClient()
