import httpx
from typing import Optional

class HttpClient:
    client: Optional[httpx.AsyncClient] = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls.client is None:
            cls.client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=50, max_connections=100)
            )
        return cls.client

    @classmethod
    async def close_client(cls) -> None:
        if cls.client:
            await cls.client.aclose()
            cls.client = None