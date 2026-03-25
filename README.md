# 🤖 RPA Legacy Freight Bridge

An unattended Robotic Process Automation (RPA) integration designed to bridge modern supply chain analytics with legacy, non-API freight carriers.

## 🎯 The Business Problem
Modern supply chain orchestration tools (like the **Digital Capacity Optimizer**) rely heavily on REST APIs for automated fleet procurement. However, a significant portion of regional carriers still operate via legacy web portals without API exposure, creating a "digital disconnect" that requires manual data entry.

## 🚀 The Solution
This project acts as the hyperautomation layer within a broader logistics ecosystem. It functions as a "Digital Worker" that:
1. **Listens:** Monitors a UiPath Orchestrator Queue for capacity procurement webhooks sent by the central AI brain.
2. **Navigates:** Automates browser sessions to log into simulated legacy carrier portals.
3. **Translates:** Converts JSON webhook payloads into UI keystrokes to execute the booking.
4. **Validates:** Scrapes the resulting confirmation ID and updates the central PostgreSQL database.

## 🛠️ Technology Stack
* **Python / FastAPI:** Webhook generation and API authentication.
* **UiPath Studio:** REFramework workflow development and UI automation.
* **UiPath Automation Cloud:** Enterprise queue management and Unattended Robot orchestration.