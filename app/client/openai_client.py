from openai import OpenAI, AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from loguru import logger
from app.core.config import settings

class OpenAIClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)

            # 1. 初始化同步客户端 (给定时任务、Service层用)
            cls._instance.sync_client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )

            # 2. 初始化异步客户端 (给 API 路由层用，高并发)
            cls._instance.async_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )
        return cls._instance

    # --- 同步方法 (Sync) ---
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    def chat_completion_sync(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        """
        同步调用：用于 Service 层或定时任务 (BackgroundScheduler)
        """
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API Key missing")
            return "Error: No API Key"

        try:
            response = self.sync_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI Sync Call Failed: {e}")
            raise e

    # --- 异步方法 (Async) ---
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    async def chat_completion_async(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        """
        异步调用：用于 FastAPI 路由层 (async def) 以提升并发性能
        """
        if not settings.OPENAI_API_KEY:
            return "Error: No API Key"

        try:
            response = await self.async_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI Async Call Failed: {e}")
            raise e

openai_client = OpenAIClient()
