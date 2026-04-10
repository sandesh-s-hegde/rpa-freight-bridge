from enum import Enum


class ApiVersion(str, Enum):
    V1 = "/api/v1"


class QueuePriority(str, Enum):
    HIGH = "High"
    NORMAL = "Normal"
    LOW = "Low"


UIPATH_AUTH_URL = "https://cloud.uipath.com/identity_/connect/token"
REQUEST_TIMEOUT_SECONDS = 30.0
