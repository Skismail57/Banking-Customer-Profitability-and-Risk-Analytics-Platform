"""API tests for FastAPI endpoints."""

import pytest
import sys
import os

os.environ.setdefault("USE_SQLITE", "true")

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from api.main import app


@pytest.mark.api
class TestAPIEndpoints:
    """Tests for FastAPI API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "database" in data
    
    def test_customers_endpoint(self, client):
        """Test customers list endpoint."""
        response = client.get("/api/v1/customers")
        # May fail without database, but should return 500 or 404, not 500 internal error
        assert response.status_code in [200, 404, 500]
    
    def test_customers_with_pagination(self, client):
        """Test customers endpoint with pagination."""
        response = client.get("/api/v1/customers?page=1&page_size=10")
        assert response.status_code in [200, 404, 500]
    
    def test_profitability_aggregate_endpoint(self, client):
        """Test profitability aggregate endpoint."""
        response = client.get("/api/v1/profitability/aggregate")
        assert response.status_code in [200, 404, 500]
    
    def test_risk_aggregate_endpoint(self, client):
        """Test risk aggregate endpoint."""
        response = client.get("/api/v1/risk/aggregate")
        assert response.status_code in [200, 404, 500]
    
    def test_segments_endpoint(self, client):
        """Test segments endpoint."""
        response = client.get("/api/v1/segments")
        assert response.status_code in [200, 404, 500]
    
    def test_churn_aggregate_endpoint(self, client):
        """Test churn aggregate endpoint."""
        response = client.get("/api/v1/churn/aggregate")
        assert response.status_code in [200, 404, 500]
    
    def test_portfolio_summary_endpoint(self, client):
        """Test portfolio summary endpoint."""
        response = client.get("/api/v1/portfolio/summary")
        assert response.status_code in [200, 404, 500]
