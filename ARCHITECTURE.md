# 🏛️ System Architecture: The RPA Bridge

This project leverages the UiPath Community Edition to demonstrate enterprise-grade hyperautomation at zero infrastructure cost.

## The Data Flow
1. **The Brain (FastAPI/Python):** The Digital Capacity Optimizer detects a capacity shortage.
2. **The Handshake (OAuth 2.0):** The Python backend authenticates with the UiPath Automation Cloud API.
3. **The Queue (Orchestrator):** Python pushes a JSON payload (Pickup, Dates, Vehicle) to the Orchestrator Queue.
4. **The Execution (Unattended Bot):** The REFramework bot picks up the queue item, navigates the legacy web portal, and executes the booking.
5. **The Callback:** The bot updates the central PostgreSQL database with the confirmation ID.

## Infrastructure Stack
* **Development:** UiPath Studio Community
* **Management:** UiPath Automation Cloud (Free Tier)
* **API Auth:** UiPath External Applications (OAuth)