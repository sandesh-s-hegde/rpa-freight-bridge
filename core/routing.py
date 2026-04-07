import os
import logging

logger = logging.getLogger("rpa-bridge")

class CarrierRouter:
    @staticmethod
    def resolve_queue(carrier_name: str) -> str:
        routing_map = {
            "MAERSK": os.getenv("UIPATH_QUEUE_MAERSK", "LGCY_MAERSK_PROD"),
            "HAPAG-LLOYD": os.getenv("UIPATH_QUEUE_HAPAG", "LGCY_HAPAG_PROD"),
            "DB_SCHENKER": os.getenv("UIPATH_QUEUE_SCHENKER", "LGCY_SCHENKER_PROD")
        }

        normalized_name = carrier_name.strip().upper()
        target_queue = routing_map.get(normalized_name)

        if not target_queue:
            default_queue = os.getenv("UIPATH_QUEUE_DEFAULT", "LGCY_DEFAULT_PROD")
            logger.warning(f"No explicit routing rule for carrier '{carrier_name}'. Falling back to {default_queue}.")
            return default_queue

        return target_queue