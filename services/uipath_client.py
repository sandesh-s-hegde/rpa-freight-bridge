import os
import httpx
from fastapi import HTTPException, status


class UiPathService:
    def __init__(self):
        self.base_url = os.getenv("UIPATH_BASE_URL")
        self.client_id = os.getenv("UIPATH_CLIENT_ID")
        self.client_secret = os.getenv("UIPATH_CLIENT_SECRET")
        self.folder_id = os.getenv("UIPATH_FOLDER_ID")
        self.queue_name = os.getenv("UIPATH_QUEUE_NAME")
        self.auth_url = "https://cloud.uipath.com/identity_/connect/token"

    async def _get_access_token(self) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.auth_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "OR.Queues OR.Queues.Write"
                }
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="UiPath authentication failed"
                )
            return response.json().get("access_token")

    async def push_to_queue(self, payload: dict) -> bool:
        token = await self._get_access_token()
        endpoint = f"{self.base_url}/odata/Queues/UiPathODataSvc.AddQueueItem"

        headers = {
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitId": self.folder_id,
            "Content-Type": "application/json"
        }

        data = {
            "itemData": {
                "Name": self.queue_name,
                "Priority": "High",
                "SpecificContent": payload
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint, headers=headers, json=data)
            if response.status_code != 201:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to enqueue transaction"
                )
            return True