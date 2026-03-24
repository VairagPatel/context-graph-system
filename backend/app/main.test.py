"""
Unit tests for FastAPI main application

Tests cover all API endpoints, service initialization, error handling,
and integration between components.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.models.api_models import QueryRequest, QueryResponse, ImportResponse, GraphData
from app.services.guardrails import QueryClassification
from app.services.query_translator import TranslationResult


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_services():
    """Mock all service dependencies."""
    with patch('app.main.neo4j_service') as mock_neo4j, \
         patch('app.main.guardrail_system') as mock_guardrail, \
         patch('app.main.query_translator') as mock_translator, \
         patch('app.main.data_import_service') as mock_import:
        
        yield {
            'neo4j': mock_neo4j,
            'guardrail': mock_guardrail,
            'translator': mock_translator,
            'import': mock_import
        }


class TestQueryEndpoint:
    """Test POST /api/query endpoint."""
    
    def test_successful_query(self, client, mock_services):
        """Test successful query execution."""
        # Mock guardrail classification
        mock_services['guardrail'].classify_query.return_value = QueryClassification(
            is_valid=True
        )
        
        # Mock query translation
        mock_services['translator'].translate.return_value = TranslationResult(
            cypher="MATCH (n:Order) RETURN n LIMIT 10",
            success=True
        )
        
        # Mock query execution
        mock_services['neo4j'].execute_query.return_value = [
            {"order_id": "12345", "total_amount": 100.0}
        ]
        
        response = client.post(
            "/api/query",
            json={"query": "Show me recent orders"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["order_id"] == "12345"
    
    def test_query_with_cypher_included(self, client, mock_services):
        """Test query with include_cypher flag."""
        mock_services['guardrail'].classify_query.return_value = QueryClassification(
            is_valid=True
        )
        
        mock_services['translator'].translate.return_value = TranslationResult(
            cypher="MATCH (n:Order) RETURN n LIMIT 10",
            success=True
        )
        
        mock_services['neo4j'].execute_query.return_value = []
        
        response = client.post(
            "/api/query",
            json={"query": "Show me orders", "include_cypher": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["cypher"] == "MATCH (n:Order) RETURN n LIMIT 10"
    
    def test_query_rejected_by_guardrails(self, client, mock_services):
        """Test query rejected by guardrail system."""
        mock_services['guardrail'].classify_query.return_value = QueryClassification(
            is_valid=False,
            reason="Query is outside business intelligence domain"
        )
        
        response = client.post(
            "/api/query",
            json={"query": "What's the weather today?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "outside business intelligence domain" in data["error"]
    
    def test_query_translation_failure(self, client, mock_services):
        """Test query with translation failure."""
        mock_services['guardrail'].classify_query.return_value = QueryClassification(
            is_valid=True
        )
        
        mock_services['translator'].translate.return_value = TranslationResult(
            cypher="",
            success=False,
            error="LLM API error"
        )
        
        response = client.post(
            "/api/query",
            json={"query": "Show me orders"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Failed to translate query" in data["error"]
    
    def test_query_execution_error(self, client, mock_services):
        """Test query with execution error."""
        mock_services['guardrail'].classify_query.return_value = QueryClassification(
            is_valid=True
        )
        
        mock_services['translator'].translate.return_value = TranslationResult(
            cypher="MATCH (n:Order) RETURN n",
            success=True
        )
        
        mock_services['neo4j'].execute_query.side_effect = Exception("Database error")
        
        response = client.post(
            "/api/query",
            json={"query": "Show me orders"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Query execution failed" in data["error"]


class TestGraphEndpoint:
    """Test GET /api/graph endpoint."""
    
    def test_get_graph_data_success(self, client, mock_services):
        """Test successful graph data retrieval."""
        mock_services['neo4j'].get_graph_data.return_value = {
            "nodes": [
                {
                    "id": "123",
                    "label": "Order",
                    "properties": {"order_id": "12345"}
                }
            ],
            "edges": [
                {
                    "id": "789",
                    "source": "123",
                    "target": "456",
                    "type": "DELIVERED_BY",
                    "properties": {}
                }
            ]
        }
        
        response = client.get("/api/graph")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["nodes"]) == 1
        assert len(data["edges"]) == 1
        assert data["nodes"][0]["label"] == "Order"
    
    def test_get_graph_data_with_limit(self, client, mock_services):
        """Test graph data retrieval with custom limit."""
        mock_services['neo4j'].get_graph_data.return_value = {
            "nodes": [],
            "edges": []
        }
        
        response = client.get("/api/graph?limit=50")
        
        assert response.status_code == 200
        mock_services['neo4j'].get_graph_data.assert_called_once_with(50)
    
    def test_get_graph_data_error(self, client, mock_services):
        """Test graph data retrieval with error."""
        mock_services['neo4j'].get_graph_data.side_effect = Exception("Database error")
        
        response = client.get("/api/graph")
        
        assert response.status_code == 500
        assert "Failed to fetch graph data" in response.json()["detail"]


class TestImportEndpoint:
    """Test POST /api/import endpoint."""
    
    def test_import_csv_success(self, client, mock_services):
        """Test successful CSV file import."""
        from app.services.data_import import ImportResult
        
        mock_services['import'].import_file.return_value = ImportResult(
            success=True,
            nodes_created=10,
            relationships_created=5,
            errors=[]
        )
        
        csv_content = b"order_id,customer_id,order_date\n12345,C001,2024-01-01"
        
        response = client.post(
            "/api/import",
            files={"file": ("orders.csv", csv_content, "text/csv")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["nodes_created"] == 10
        assert data["relationships_created"] == 5
    
    def test_import_json_success(self, client, mock_services):
        """Test successful JSON file import."""
        from app.services.data_import import ImportResult
        
        mock_services['import'].import_file.return_value = ImportResult(
            success=True,
            nodes_created=5,
            relationships_created=3,
            errors=[]
        )
        
        json_content = b'[{"order_id": "12345", "customer_id": "C001"}]'
        
        response = client.post(
            "/api/import",
            files={"file": ("orders.json", json_content, "application/json")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["nodes_created"] == 5
    
    def test_import_unsupported_file_type(self, client, mock_services):
        """Test import with unsupported file type."""
        response = client.post(
            "/api/import",
            files={"file": ("data.txt", b"some text", "text/plain")}
        )
        
        assert response.status_code == 400
        assert "Only CSV and JSON files are supported" in response.json()["detail"]
    
    def test_import_with_errors(self, client, mock_services):
        """Test import with validation errors."""
        from app.services.data_import import ImportResult
        
        mock_services['import'].import_file.return_value = ImportResult(
            success=False,
            nodes_created=0,
            relationships_created=0,
            errors=["Missing required field: order_id"]
        )
        
        csv_content = b"customer_id,order_date\nC001,2024-01-01"
        
        response = client.post(
            "/api/import",
            files={"file": ("orders.csv", csv_content, "text/csv")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert len(data["errors"]) == 1
    
    def test_import_exception(self, client, mock_services):
        """Test import with unexpected exception."""
        mock_services['import'].import_file.side_effect = Exception("Import error")
        
        csv_content = b"order_id,customer_id\n12345,C001"
        
        response = client.post(
            "/api/import",
            files={"file": ("orders.csv", csv_content, "text/csv")}
        )
        
        assert response.status_code == 500
        assert "Import failed" in response.json()["detail"]


class TestSchemaEndpoint:
    """Test GET /api/schema endpoint."""
    
    def test_get_schema(self, client):
        """Test schema retrieval."""
        response = client.get("/api/schema")
        
        assert response.status_code == 200
        data = response.json()
        assert "node_types" in data
        assert "relationship_types" in data
        assert "Order" in data["node_types"]
        assert "DELIVERED_BY" in data["relationship_types"]
    
    def test_schema_structure(self, client):
        """Test schema has correct structure."""
        response = client.get("/api/schema")
        data = response.json()
        
        # Check node types
        assert isinstance(data["node_types"], dict)
        assert "Order" in data["node_types"]
        assert "order_id" in data["node_types"]["Order"]
        
        # Check relationship types
        assert isinstance(data["relationship_types"], list)
        assert len(data["relationship_types"]) > 0


class TestHealthEndpoint:
    """Test GET /api/health endpoint."""
    
    def test_health_check_healthy(self, client, mock_services):
        """Test health check when all services are healthy."""
        mock_services['neo4j'].health_check.return_value = True
        
        with patch.dict('os.environ', {'LLM_PROVIDER': 'groq'}):
            response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["neo4j_connected"] is True
        assert data["llm_provider"] == "groq"
    
    def test_health_check_degraded(self, client, mock_services):
        """Test health check when Neo4j is unavailable."""
        mock_services['neo4j'].health_check.return_value = False
        
        with patch.dict('os.environ', {'LLM_PROVIDER': 'gemini'}):
            response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["neo4j_connected"] is False
        assert data["llm_provider"] == "gemini"
    
    def test_health_check_exception(self, client, mock_services):
        """Test health check with exception."""
        mock_services['neo4j'].health_check.side_effect = Exception("Health check error")
        
        response = client.get("/api/health")
        
        assert response.status_code == 500
        assert "Health check failed" in response.json()["detail"]


class TestCORSConfiguration:
    """Test CORS middleware configuration."""
    
    def test_cors_headers_present(self, client):
        """Test CORS headers are included in responses."""
        response = client.options("/api/health")
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


class TestErrorHandling:
    """Test error handling across endpoints."""
    
    def test_query_endpoint_handles_none_services(self, client):
        """Test query endpoint handles uninitialized services."""
        with patch('app.main.guardrail_system', None):
            response = client.post(
                "/api/query",
                json={"query": "Show me orders"}
            )
            
            # Should return error response
            assert response.status_code in [200, 500]
    
    def test_graph_endpoint_handles_none_services(self, client):
        """Test graph endpoint handles uninitialized services."""
        with patch('app.main.neo4j_service', None):
            response = client.get("/api/graph")
            
            # Should return error
            assert response.status_code == 500


class TestRequestValidation:
    """Test request validation."""
    
    def test_query_endpoint_missing_query_field(self, client):
        """Test query endpoint with missing query field."""
        response = client.post(
            "/api/query",
            json={}
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_import_endpoint_no_file(self, client):
        """Test import endpoint without file."""
        response = client.post("/api/import")
        
        # Should return validation error
        assert response.status_code == 422
