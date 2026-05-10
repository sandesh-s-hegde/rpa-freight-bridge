import hashlib
import hmac
import logging
import os
import secrets
from typing import Optional

from fastapi import HTTPException, Request, Security, status
from fastapi.security.api_key import APIKeyHeader

logger = logging.getLogger("rpa-bridge")

# 1. Standard API Key Authentication
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """Validates standard API requests against timing attacks."""
    expected_key = os.getenv("API_SECRET_KEY", "dev_api_secret_key")

    if not api_key or not secrets.compare_digest(api_key, expected_key):
        logger.warning("Rejected request: Invalid or missing API Key.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing API Key"
        )
    return api_key


# 2. Cryptographic Webhook Validation
async def verify_webhook_signature(request: Request) -> None:
    """Cryptographically verifies inbound webhook payloads from freight partners."""
    secret = os.getenv("WEBHOOK_SECRET_KEY", "dev_webhook_secret").encode("utf-8")
    signature_header = request.headers.get("X-RPA-Signature")

    if not signature_header:
        logger.warning("Rejected webhook: Missing X-RPA-Signature header.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing cryptographic signature.",
        )

    body = await request.body()
    expected_signature = hmac.new(secret, body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_signature, signature_header):
        logger.error("Rejected webhook: Cryptographic signature mismatch.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid payload signature."
        )
