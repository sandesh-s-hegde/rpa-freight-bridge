# 🤖 RPA Legacy Freight Bridge: Hyperautomation API

**Author:** Sandesh S. Hegde  
**Version:** v1.0.0 (Enterprise Integration Edition)  

## 📖 Executive Summary

This artifact operationalizes the execution layer of the supply chain ecosystem. It serves as a **Hyperautomation Bridge**, designed to connect modern, AI-driven supply chain analytics (like the Digital Capacity Optimizer) with legacy, non-API freight carriers. By functioning as a high-throughput "Digital Worker," this microservice translates JSON webhook payloads into simulated browser keystrokes via UiPath, entirely eliminating manual data entry for legacy portal bookings.

---

## 🎯 The Business Problem

Modern supply chain orchestration tools rely heavily on REST APIs for automated fleet procurement. However, a significant portion of regional logistics providers still operate via legacy web portals without API exposure. This creates a "digital disconnect," forcing supply chain planners to manually extract AI-recommended bookings and type them into carrier websites — a slow, error-prone, and unscalable process.

---

## 🧮 Architectural Framework

This microservice acts as the intelligent middleware router. It is built on a strictly asynchronous, event-driven architecture:

### 1. Asynchronous Ingestion & Idempotency
To prevent UI blocking on the central AI system, the API utilizes a **Background Task Execution** model. Incoming webhooks are immediately validated and returned with a `202 Accepted` status. An idempotent repository layer ensures that duplicate `transaction_id` requests caused by network retries are silently dropped, preventing redundant (and costly) truck bookings.

### 2. Connection Pooling & Resource Optimization
External API calls to the UiPath Orchestrator are optimized using a **Singleton HTTPX Connection Pool** and **In-Memory OAuth Token Caching**. This drastically reduces TLS handshake latency and prevents rate-limiting from the UiPath Identity server.

### 3. Distributed Observability
The system implements **Contextual Correlation IDs** (`X-Correlation-ID`) across all requests, logging them in a structured JSON format. This enables end-to-end distributed tracing across the FastAPI backend, the PostgreSQL database, and the UiPath Orchestrator queue.

### 4. Robotic Execution Layer
The API pushes standardized payloads into a high-priority UiPath Orchestrator Queue. An Unattended Robot (built via the REFramework) monitors this queue, automatically launches a headless browser, navigates the legacy carrier UI, and executes the transaction.

---

## 🚀 Key Features

### 🛡️ 1. Enterprise Security & Resilience
* **Strict Validation:** `pydantic` schemas enforce strict data typing for incoming capacity requests.
* **Rate Limiting:** `slowapi` protects the webhook endpoint from DDoS or runaway retry loops.
* **Network Resilience:** `tenacity` provides exponential backoff and retry logic for external UiPath API calls.

### 📊 2. Deep Health & Telemetry
* **Prometheus Integration:** Exposes a `/metrics` endpoint for real-time scraping of request rates, latencies, and error distributions.
* **Deep Database Probes:** The health check endpoint actively pings the connection pool to verify operational readiness, not just server uptime.

### 💾 3. State Management & Auditability
* **Async PostgreSQL Engine:** Utilizes `asyncpg` and SQLAlchemy 2.0 for non-blocking database operations.
* **Paginated Retrieval:** A dedicated `/api/v1/audit` endpoint allows stakeholders to query the operational history of all processed webhooks.

---

## ⚙️ Technical Architecture

* **Language:** Python 3.11+
* **Framework:** FastAPI (Asynchronous ASGI)
* **Database:** PostgreSQL 15 (via `asyncpg` & `SQLAlchemy`)
* **RPA Engine:** UiPath Automation Cloud & Unattended Robots
* **Observability:** Prometheus FastApi Instrumentator & Python JSON Logger
* **DevOps:** Docker Compose, GitHub Actions (CI/CD), Pre-commit hooks

---

## 🚀 Installation & Usage

### Prerequisites
You need [Docker & Docker Compose](https://www.docker.com/) installed on your machine.

### Local Deployment

```bash
# 1. Clone the repository
git clone https://github.com/sandesh-s-hegde/rpa-freight-bridge.git
cd rpa-freight-bridge

# 2. Set your Environment Variables
# Create a .env file and populate it using .env.example
cp .env.example .env

# 3. Build and launch the multi-container environment (API + PostgreSQL)
make docker-up

# 4. Verify System Health
curl http://localhost:8000/api/v1/system/health
```

### Developer Commands
A `Makefile` is included to standardize workflows:
* `make install` - Installs Python requirements.
* `make run` - Runs the application locally via Uvicorn.
* `make test` - Executes the `pytest` suite.

---

## ☁️ Production Infrastructure

This application is designed for containerized deployment in environments like Kubernetes, AWS ECS, or Render. 
* **Compute:** Containerized FastAPI web service.
* **Storage:** Dedicated PostgreSQL instance linked via `DATABASE_URL`.
* **CI/CD:** Automated linting (`ruff`), formatting, and dependency validation via GitHub Actions on every push to `main`.

---

## 📄 Citation

If you reference this architectural pattern, please cite it as follows:

**Harvard Style:**
> Hegde, S.S. (2026). RPA Legacy Freight Bridge: Hyperautomation API (Version 1.0.0) [Software]. Available at: https://github.com/sandesh-s-hegde/rpa-freight-bridge

**BibTeX:**
```bibtex
@software{Hegde_RPA_Freight_Bridge_2026,
  author = {Hegde, Sandesh Subramanya},
  month = apr,
  title = {RPA Legacy Freight Bridge: Hyperautomation API},
  url = {[https://github.com/sandesh-s-hegde/rpa-freight-bridge](https://github.com/sandesh-s-hegde/rpa-freight-bridge)},
  version = {1.0.0},
  year = {2026}
}
```

---

## 🔮 Roadmap & Project Status

This project is structured for incremental enterprise scale, moving from a foundational one-way API to a fully cognitive, distributed event-driven ecosystem.

| Phase | Maturity Level | Key Capabilities | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Foundation (v1.0)** | **Async API Gateway, Idempotent PostgreSQL persistence, Connection Pooling, Telemetry, and 1-Way Queue Dispatch.** | ✅ **Stable** |
| **Phase 2** | **Closed-Loop Execution** | Bidirectional webhooks. The RPA bot reports final confirmation IDs back to the FastAPI gateway to update the AI's state. | 🚧 Next |
| **Phase 3** | **Multi-Tenant Dispatch** | "Factory Pattern" routing. The API dynamically routes payloads to different dedicated UiPath queues based on the `carrier_name`. | 🚧 Planned |
| **Phase 4** | **Cognitive Processing (IDP)** | Integration with UiPath Document Understanding/OCR to ingest unstructured legacy PDF invoices and email bookings. | 💡 Vision |
| **Phase 5** | **Event Streaming** | Migration from background tasks to Apache Kafka / AWS SQS for high-availability, globally distributed webhook ingestion. | 💡 Vision |

---

> ➡️ **Ecosystem Integration:** This repository acts as the "hands" of the logistics ecosystem. The brain dictating these actions is the **[Digital Capacity Optimizer](https://github.com/sandesh-s-hegde/digital_capacity_optimizer)**, which calculates the multi-modal routing logic and dispatches the webhooks processed by this API.