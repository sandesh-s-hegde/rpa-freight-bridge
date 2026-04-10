import time
import logging
from functools import wraps
from fastapi import HTTPException, status

logger = logging.getLogger("rpa-bridge")


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    logger.info("Circuit Breaker: Transitioned to HALF_OPEN state.")
                else:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Circuit breaker is OPEN. Upstream RPA service is degraded.",
                    )

            try:
                result = await func(*args, **kwargs)
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                    logger.info(
                        "Circuit Breaker: Recovered and transitioned to CLOSED state."
                    )
                return result
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    logger.error(
                        "Circuit Breaker: Tripped to OPEN state due to consecutive upstream failures."
                    )
                raise e

        return wrapper


uipath_circuit_breaker = CircuitBreaker()
