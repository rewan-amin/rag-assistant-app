from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_query_happy_path():
    # Mock retrieval and generation services on app.state
    mock_retrieval = MagicMock()
    mock_retrieval.retrieve.return_value = [
        {"chunk_id": "c1", "text": "Refund policy text.", "source": "policy.pdf", "page": 1, "score": 0.95}
    ]

    mock_generation = MagicMock()
    mock_generation.generate_answer.return_value = (
        "Refunds are allowed within 30 days as stated in policy.pdf.",
        ["policy.pdf"]
    )

    app.state.retrieval_service = mock_retrieval
    app.state.generation_service = mock_generation

    payload = {"question": "What is the refund policy?"}
    response = client.post("/query", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert data["answer"] == "Refunds are allowed within 30 days as stated in policy.pdf."
    assert data["sources"] == ["policy.pdf"]
    assert data.get("detections") is None

def test_query_invalid_input():
    # POST /query without question field -> 422
    payload = {}
    response = client.post("/query", json=payload)
    assert response.status_code == 422

    # POST /query with empty string question -> 422
    payload_empty = {"question": "   "}
    response_empty = client.post("/query", json=payload_empty)
    assert response_empty.status_code == 422
