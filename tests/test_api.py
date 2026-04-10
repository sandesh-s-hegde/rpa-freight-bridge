from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

def test_unauthorized_orchestration_trigger():
    payload = {
        "transaction_id": "TEST-123",
        "carrier_name": "Test Carrier",
        "vehicle_type": "Truck",
        "pickup_date": "2026-04-01",
        "max_budget_eur": 500.0
    }
    response = client.post("/api/v1/orchestrate", json=payload)
    assert response.status_code == 403