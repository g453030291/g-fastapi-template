import httpx
from tenacity import retry, stop_after_attempt, wait_random_exponential


class HttpClient:
    def __init__(self):
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )

    async def aclose(self):
        await self._client.aclose()

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self._client.get(url, **kwargs)

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self._client.post(url, **kwargs)

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
    async def put(self, url: str, **kwargs) -> httpx.Response:
        return await self._client.put(url, **kwargs)

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
    async def delete(self, url: str, **kwargs) -> httpx.Response:
        return await self._client.delete(url, **kwargs)


http_client = HttpClient()
