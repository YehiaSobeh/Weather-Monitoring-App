"""Edge‑case UI tests for user register/login endpoints."""
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)
API = "/api/v1"

def _unique_email():
    return f"{uuid.uuid4().hex}@example.com"
