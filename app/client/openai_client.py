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

            # 1. 初始化同步客户端
            cls._instance.sync_client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )

            # 2. 初始化异步客户端
            cls._instance.async_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )
        return cls._instance

    def _prepare_args(self, prompt: str, system_prompt: str, model: str | None, temperature: float, json_mode: bool) -> \
    Dict[str, Any]:
        """
        内部辅助方法：统一构造请求参数，避免 Sync/Async 代码重复
        """
        # 1. 确定模型：如果传入了 model 则用传入的，否则用配置文件里的默认值
        use_model = model if model else settings.OPENAI_MODEL

        # 2. 防坑处理：JSON 模式必须在 Prompt 里包含 "json" 字样
        if json_mode and "json" not in system_prompt.lower():
            system_prompt = f"{system_prompt} (Please output in JSON format)"

        # 3. 构造基础参数
        kwargs = {
            "model": use_model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        }

        # 4. 注入 JSON 模式配置
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        return kwargs

    def _parse_response(self, content: str, json_mode: bool) -> Union[str, Dict[str, Any]]:
        """
        内部辅助方法：统一处理响应解析
        """
        if json_mode:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logger.error(f"JSON 解析失败，返回原始字符串: {content}")
                return content
        return content

    # --- 同步方法 (Sync) ---
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    def chat_sync(
            self,
            prompt: str,
            system_prompt: str = "You are a helpful assistant.",
            model: str = None,  # 新增：允许覆盖模型
            temperature: float = 0.7,  # 新增：温度控制
            json_mode: bool = False  # 建议保留：控制是否强制 JSON
    ) -> Union[str, Dict[str, Any]]:

        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API Key missing")
            return {} if json_mode else "Error: No API Key"

        try:
            # 构造参数
            kwargs = self._prepare_args(prompt, system_prompt, model, temperature, json_mode)

            # 发起请求
            response = self.sync_client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content

            # 解析结果
            return self._parse_response(content, json_mode)

        except Exception as e:
            logger.error(f"OpenAI Sync Call Failed: {e}")
            raise e

    # --- 异步方法 (Async) ---
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
            # 构造参数
            kwargs = self._prepare_args(prompt, system_prompt, model, temperature, json_mode)

            # 发起请求 (await)
            response = await self.async_client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content

            # 解析结果
            return self._parse_response(content, json_mode)

        except Exception as e:
            logger.error(f"OpenAI Async Call Failed: {e}")
            raise e


openai_client = OpenAIClient()
