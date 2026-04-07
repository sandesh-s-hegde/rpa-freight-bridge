import os
import time
from fastapi import HTTPException, status
from tenacity import retry, stop_after_attempt, wait_exponential
from core.http_client import HttpClient


class UiPathService:
    _token_cache: str | None = None
    _token_expires_at: float = 0.0

    def __init__(self):
        self.base_url = os.getenv("UIPATH_BASE_URL")
        self.client_id = os.getenv("UIPATH_CLIENT_ID")
        self.client_secret = os.getenv("UIPATH_CLIENT_SECRET")
        self.folder_id = os.getenv("UIPATH_FOLDER_ID")
        self.auth_url = "https://cloud.uipath.com/identity_/connect/token"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _get_access_token(self) -> str:
        if self._token_cache and time.time() < self._token_expires_at:
            return self._token_cache

        client = HttpClient.get_client()
        response = await client.post(
            self.auth_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "OR.Queues OR.Queues.Write"
            }
        )
        response.raise_for_status()
        data = response.json()

        self.__class__._token_cache = data.get("access_token")
        self.__class__._token_expires_at = time.time() + data.get("expires_in", 3600) - 60

        return self._token_cache

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def push_to_queue(self, payload: dict, target_queue: str) -> bool:
        token = await self._get_access_token()
        endpoint = f"{self.base_url}/odata/Queues/UiPathODataSvc.AddQueueItem"

        headers = {
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitId": self.folder_id,
            "Content-Type": "application/json"
        }

        data = {
            "itemData": {
                "Name": target_queue,
                "Priority": "High",
                "SpecificContent": payload
            }
        }

        client = HttpClient.get_client()
        response = await client.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.status_code == 201