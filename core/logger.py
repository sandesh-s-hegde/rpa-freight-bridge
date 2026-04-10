import logging
import sys
from pythonjsonlogger import jsonlogger
from core.context import correlation_id_ctx


class PiiRedactingFormatter(jsonlogger.JsonFormatter):
    SENSITIVE_KEYS = {"max_budget_eur", "client_secret", "access_token"}

    def process_log_record(self, log_record):
        for key in list(log_record.keys()):
            if key in self.SENSITIVE_KEYS:
                log_record[key] = "***REDACTED***"
        return super().process_log_record(log_record)


class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_ctx.get()
        return True


def get_logger(name: str = "rpa-bridge") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = PiiRedactingFormatter(
            "%(asctime)s %(name)s %(levelname)s %(correlation_id)s %(message)s",
            rename_fields={"levelname": "level", "asctime": "timestamp"},
        )
        handler.setFormatter(formatter)
        handler.addFilter(CorrelationIdFilter())
        logger.addHandler(handler)

    return logger
