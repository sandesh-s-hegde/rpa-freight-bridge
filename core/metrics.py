from prometheus_client import Counter

RPA_TASKS_DISPATCHED = Counter(
    "rpa_tasks_dispatched_total",
    "Total number of webhook payloads routed to UiPath Orchestrator",
    ["carrier_name"]
)

RPA_TASKS_COMPLETED = Counter(
    "rpa_tasks_completed_total",
    "Total number of successful callbacks received from Unattended Robots",
    ["status"]
)