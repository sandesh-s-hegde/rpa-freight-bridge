import hmac
import hashlib
import os
import logging
from fastapi import Request, HTTPException, status

logger = logging.getLogger("rpa-bridge")


async def verify_webhook_signature(request: Request) -> None:
    secret = os.getenv("WEBHOOK_SECRET_KEY", "dev_secret_key").encode("utf-8")
    signature_header = request.headers.get("X-RPA-Signature")

    if not signature_header:
        logger.warning("Rejected callback: Missing X-RPA-Signature header.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing cryptographic signature.",
        )

    body = await request.body()
    expected_signature = hmac.new(secret, body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_signature, signature_header):
        logger.error("Rejected callback: Cryptographic signature mismatch.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid payload signature."
        )
