import os
import requests


def add_queue_item_to_uipath(payload: dict) -> bool:
    """Pushes a capacity procurement payload to the UiPath Orchestrator Queue via OAuth 2.0."""
    auth_url = "https://cloud.uipath.com/identity_/connect/token"
    token_response = requests.post(auth_url, data={
        "grant_type": "client_credentials",
        "client_id": os.getenv("UIPATH_CLIENT_ID"),
        "client_secret": os.getenv("UIPATH_CLIENT_SECRET"),
        "scope": "OR.Queues OR.Queues.Write"
    })

    access_token = token_response.json().get("access_token")

    orchestrator_url = f"{os.getenv('UIPATH_BASE_URL')}/odata/Queues/UiPathODataSvc.AddQueueItem"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-UIPATH-OrganizationUnitId": os.getenv("UIPATH_FOLDER_ID"),
        "Content-Type": "application/json"
    }

    queue_data = {
        "itemData": {
            "Name": os.getenv("UIPATH_QUEUE_NAME"),
            "Priority": "High",
            "SpecificContent": payload
        }
    }

    response = requests.post(orchestrator_url, headers=headers, json=queue_data)
    return response.status_code == 201