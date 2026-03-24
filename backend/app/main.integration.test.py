"""
Integration tests for FastAPI API endpoints

These tests verify the complete integration of API endpoints with all services,
testing realistic scenarios including valid/invalid queries, different limit values,
file imports, and error handling.

**Validates: Requirements 4.1, 4.2, 4.3, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7**
"""

import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.guardrails import QueryClassification
from app.services.query_translator import TranslationResult
from app.services.data_import import ImportResult


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_services():
    """Mock all service dependencies for integration tests."""
    with patch('app.main.neo4j_service') as mock_neo4j, \
         patch('app.main.guardrail_system') as mock_guardrail, \
         patch('app.main.query_translator') as mock_translator, \
         patch('app.main.data_import_service') as mock_import:
        
        # Set up default behaviors
        mock_neo4j.health_check.return_value = True
        
        yield {
            'neo4j': mock_neo4j,
            'guardrail': mock_guardrail,
            'translator': mock_translator,
            'import': mock_import
        }


class TestQueryEndpointIntegration:
    """Integration tests for POST /api/query endpoint."""
    
    def test_valid_query_complete_flow(self, client, mock_services):
        """Test complete flow with valid query from guardrails to results."""
        # Setup: Valid query passes guardrails
        mock_services['guardrail'].classify_query.return_value = QueryClassification(
            is_valid=True
        )
        
        # Setup: Translation succeeds
        mock_services['translator'].translate.return_value = TranslationResult(
            cypher="MATCH (o:Order) WHERE o.status = 'delivered' RETURN o.order_id, o.total_amount LIMIT 10",
            success=True
        )
        
        # Setup: Query execution returns results
        mock_services['neo4j'].execute_query.return_value = [
            {"order_id": "ORD001", "total_amount": 150.50},
            {"order_id": "ORD002", "total_amount": 200.00},
            {"order_id": "ORD003", "total_amount": 75.25}
        ]
        
        # Execute
        response = client.post(
            "/api/query",
            json={"query": "Show me delivered orders"}
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3
        assert data["data"][0]["order_id"] == "ORD001"
        assert data["data"][0]["total_amount"] == 150.50
        assert data["error"] is None
        
        # Verify service calls
        mock_services['guardrail'].classify_query.assert_called_once()
        mock_services['translator'].translate.assert_called_once()
        mock_services['neo4j'].execute_query.assert_called_once()
    
    def test_invalid_query_rejected_by_guardrails(self, client, mock_services):
        """Test invalid query rejected by guardrail system."""
        # Setup: Query fails guardrails
        mock_services['guardrail'].classify_query.return_value = QueryClassification(
            is_valid=False,
            reason="Query is outside business intelligence domain. Please ask about orders, deliveries, invoices, or payments."
        )
        
        # Execute
        response = client.post(
            "/api/query",
            json={"query": "What's the weather like today?"}
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["data"] == []
        assert "outside business intelligence domain" in data["error"]
        
        # Verify translator was NOT called
        mock_services['translator'].translate.assert_not_called()
        mock_services['neo4j'].execute_query.assert_not_called()
    
    def test_query_with_include_cypher_flag(self, client, mock_services):
        """Test query with include_cypher flag returns generated Cypher."""
        # Setup
        mock_services['guardrail'].classify_query.return_value = QueryClassification(
            is_valid=True
        )
        
        cypher_query = "MATCH (c:Customer) RETURN c.name, c.email LIMIT 5"
        mock_services['translator'].translate.return_value = TranslationResult(
            cypher=cypher_query,
            success=True
        )
        
        mock_services['neo4j'].execute_query.return_value = [
            {"name": "John Doe", "email": "john@example.com"}
        ]
        
        # Execute
        response = client.post(
            "/api/query",
            json={
                "query": "Show me customer names and emails",
                "include_cypher": True
            }
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["cypher"] == cypher_query
        assert len(data["data"]) == 1
    
    def test_query_without_include_cypher_flag(self, client, mock_services):
        """Test query without include_cypher flag does not return Cypher."""
        # Setup
        mock_services['guardrail'].classify_query.return_value = QueryClassification(
            is_valid=True
        )
        
        mock_services['translator'].translate.return_value = TranslationResult(
            cypher="MATCH (o:Order) RETURN o",
            success=True
        )
        
        mock_services['neo4j'].execute_query.return_value = []
        
        # Execute
        response = client.post(
            "/api/query",
            json={"query": "Show me orders", "include_cypher": False}
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["cypher"] is None
    
    def test_query_translation_failure(self, client, mock_services):
        """Test query when translation fails."""
        # Setup
        mock_services['guardrail'].classify_query.return_value = QueryClassification(
            is_valid=True
        )
        
        mock_services['translator'].translate.return_value = TranslationResult(
            cypher="",
            success=False,
            error="LLM API rate limit exceeded"
        )
        
        # Execute
        response = client.post(
            "/api/query",
            json={"query": "Show me complex data"}
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Failed to translate query" in data["error"]
        assert "LLM API rate limit exceeded" in data["error"]
        
        # Verify Neo4j was NOT called
        mock_services['neo4j'].execute_query.assert_not_called()
    
    def test_query_execution_database_error(self, client, mock_services):
        """Test query when database execution fails."""
        # Setup
        mock_services['guardrail'].classify_query.return_value = QueryClassification(
            is_valid=True
        )
        
        mock_services['translator'].translate.return_value = TranslationResult(
            cypher="MATCH (n) RETURN n",
            success=True
        )
        
        mock_services['neo4j'].execute_query.side_effect = Exception("Neo4j connection timeout")
        
        # Execute
        response = client.post(
            "/api/query",
            json={"query": "Show me all data"}
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Query execution failed" in data["error"]
        assert "Neo4j connection timeout" in data["error"]
    
    def test_query_returns_empty_results(self, client, mock_services):
        """Test query that returns no results."""
        # Setup
        mock_services['guardrail'].classify_query.return_value = QueryClassification(
            is_valid=True
        )
        
        mock_services['translator'].translate.return_value = TranslationResult(
            cypher="MATCH (o:Order) WHERE o.status = 'nonexistent' RETURN o",
            success=True
        )
        
        mock_services['neo4j'].execute_query.return_value = []
        
        # Execute
        response = client.post(
            "/api/query",
            json={"query": "Show me orders with nonexistent status"}
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] == []
        assert data["error"] is None
    
    def test_query_missing_required_field(self, client, mock_services):
        """Test query endpoint with missing required query field."""
        # Execute
        response = client.post(
            "/api/query",
            json={}
        )
        
        # Verify: Should return validation error
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data


class TestGraphEndpointIntegration:
    """Integration tests for GET /api/graph endpoint."""
    
    def test_graph_endpoint_default_limit(self, client, mock_services):
        """Test graph endpoint with default limit of 100."""
        # Setup
        mock_services['neo4j'].get_graph_data.return_value = {
            "nodes": [
                {"id": "n1", "label": "Order", "properties": {"order_id": "ORD001"}},
                {"id": "n2", "label": "Customer", "properties": {"customer_id": "C001"}}
            ],
            "edges": [
                {"id": "e1", "source": "n1", "target": "n2", "type": "PURCHASED_BY", "properties": {}}
            ]
        }
        
        # Execute
        response = client.get("/api/graph")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1
        assert data["nodes"][0]["label"] == "Order"
        assert data["edges"][0]["type"] == "PURCHASED_BY"
        
        # Verify default limit was used
        mock_services['neo4j'].get_graph_data.assert_called_once_with(100)
    
    def test_graph_endpoint_custom_limit_50(self, client, mock_services):
        """Test graph endpoint with custom limit of 50."""
        # Setup
        mock_services['neo4j'].get_graph_data.return_value = {
            "nodes": [],
            "edges": []
        }
        
        # Execute
        response = client.get("/api/graph?limit=50")
        
        # Verify
        assert response.status_code == 200
        mock_services['neo4j'].get_graph_data.assert_called_once_with(50)
    
    def test_graph_endpoint_custom_limit_200(self, client, mock_services):
        """Test graph endpoint with custom limit of 200."""
        # Setup
        mock_services['neo4j'].get_graph_data.return_value = {
            "nodes": [],
            "edges": []
        }
        
        # Execute
        response = client.get("/api/graph?limit=200")
        
        # Verify
        assert response.status_code == 200
        mock_services['neo4j'].get_graph_data.assert_called_once_with(200)
    
    def test_graph_endpoint_limit_1(self, client, mock_services):
        """Test graph endpoint with minimum limit of 1."""
        # Setup
        mock_services['neo4j'].get_graph_data.return_value = {
            "nodes": [{"id": "n1", "label": "Order", "properties": {}}],
            "edges": []
        }
        
        # Execute
        response = client.get("/api/graph?limit=1")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert len(data["nodes"]) == 1
        mock_services['neo4j'].get_graph_data.assert_called_once_with(1)
    
    def test_graph_endpoint_database_error(self, client, mock_services):
        """Test graph endpoint when database fails."""
        # Setup
        mock_services['neo4j'].get_graph_data.side_effect = Exception("Database connection failed")
        
        # Execute
        response = client.get("/api/graph")
        
        # Verify
        assert response.status_code == 500
        error_data = response.json()
        assert "Failed to fetch graph data" in error_data["detail"]
    
    def test_graph_endpoint_empty_graph(self, client, mock_services):
        """Test graph endpoint with empty graph."""
        # Setup
        mock_services['neo4j'].get_graph_data.return_value = {
            "nodes": [],
            "edges": []
        }
        
        # Execute
        response = client.get("/api/graph")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["nodes"] == []
        assert data["edges"] == []
    
    def test_graph_endpoint_complex_properties(self, client, mock_services):
        """Test graph endpoint with complex node and edge properties."""
        # Setup
        mock_services['neo4j'].get_graph_data.return_value = {
            "nodes": [
                {
                    "id": "n1",
                    "label": "Order",
                    "properties": {
                        "order_id": "ORD001",
                        "total_amount": 250.75,
                        "status": "delivered",
                        "order_date": "2024-01-15"
                    }
                }
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "n1",
                    "target": "n2",
                    "type": "CONTAINS",
                    "properties": {
                        "quantity": 3,
                        "unit_price": 50.25
                    }
                }
            ]
        }
        
        # Execute
        response = client.get("/api/graph")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["nodes"][0]["properties"]["total_amount"] == 250.75
        assert data["edges"][0]["properties"]["quantity"] == 3


class TestImportEndpointIntegration:
    """Integration tests for POST /api/import endpoint."""
    
    def test_import_csv_file_success(self, client, mock_services):
        """Test successful CSV file import."""
        # Setup
        mock_services['import'].import_file.return_value = ImportResult(
            success=True,
            nodes_created=15,
            relationships_created=8,
            errors=[]
        )
        
        csv_content = b"order_id,customer_id,order_date,total_amount,status\nORD001,C001,2024-01-01,100.50,delivered"
        
        # Execute
        response = client.post(
            "/api/import",
            files={"file": ("orders.csv", csv_content, "text/csv")}
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["nodes_created"] == 15
        assert data["relationships_created"] == 8
        assert data["errors"] is None
    
    def test_import_json_file_success(self, client, mock_services):
        """Test successful JSON file import."""
        # Setup
        mock_services['import'].import_file.return_value = ImportResult(
            success=True,
            nodes_created=10,
            relationships_created=5,
            errors=[]
        )
        
        json_content = json.dumps([
            {"order_id": "ORD001", "customer_id": "C001", "total_amount": 100.50},
            {"order_id": "ORD002", "customer_id": "C002", "total_amount": 200.00}
        ]).encode()
        
        # Execute
        response = client.post(
            "/api/import",
            files={"file": ("orders.json", json_content, "application/json")}
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["nodes_created"] == 10
        assert data["relationships_created"] == 5
    
    def test_import_unsupported_file_type_txt(self, client, mock_services):
        """Test import with unsupported .txt file."""
        # Execute
        response = client.post(
            "/api/import",
            files={"file": ("data.txt", b"some text data", "text/plain")}
        )
        
        # Verify
        assert response.status_code == 400
        error_data = response.json()
        assert "Only CSV and JSON files are supported" in error_data["detail"]
    
    def test_import_unsupported_file_type_xml(self, client, mock_services):
        """Test import with unsupported .xml file."""
        # Execute
        response = client.post(
            "/api/import",
            files={"file": ("data.xml", b"<data></data>", "application/xml")}
        )
        
        # Verify
        assert response.status_code == 400
        error_data = response.json()
        assert "Only CSV and JSON files are supported" in error_data["detail"]
    
    def test_import_with_validation_errors(self, client, mock_services):
        """Test import with data validation errors."""
        # Setup
        mock_services['import'].import_file.return_value = ImportResult(
            success=False,
            nodes_created=0,
            relationships_created=0,
            errors=[
                "Row 1: Missing required field 'order_id'",
                "Row 3: Invalid date format for 'order_date'"
            ]
        )
        
        csv_content = b"customer_id,order_date\nC001,invalid-date"
        
        # Execute
        response = client.post(
            "/api/import",
            files={"file": ("orders.csv", csv_content, "text/csv")}
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["nodes_created"] == 0
        assert len(data["errors"]) == 2
        assert "Missing required field" in data["errors"][0]
    
    def test_import_partial_success_with_errors(self, client, mock_services):
        """Test import with partial success and some errors."""
        # Setup
        mock_services['import'].import_file.return_value = ImportResult(
            success=True,
            nodes_created=8,
            relationships_created=4,
            errors=["Row 5: Duplicate order_id, skipped"]
        )
        
        csv_content = b"order_id,customer_id\nORD001,C001\nORD001,C002"
        
        # Execute
        response = client.post(
            "/api/import",
            files={"file": ("orders.csv", csv_content, "text/csv")}
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["nodes_created"] == 8
        assert data["errors"] is not None
        assert len(data["errors"]) == 1
    
    def test_import_no_file_provided(self, client, mock_services):
        """Test import endpoint without file."""
        # Execute
        response = client.post("/api/import")
        
        # Verify: Should return validation error
        assert response.status_code == 422
    
    def test_import_service_exception(self, client, mock_services):
        """Test import when service raises exception."""
        # Setup
        mock_services['import'].import_file.side_effect = Exception("File parsing error")
        
        csv_content = b"order_id,customer_id\nORD001,C001"
        
        # Execute
        response = client.post(
            "/api/import",
            files={"file": ("orders.csv", csv_content, "text/csv")}
        )
        
        # Verify
        assert response.status_code == 500
        error_data = response.json()
        assert "Import failed" in error_data["detail"]


class TestSchemaEndpointIntegration:
    """Integration tests for GET /api/schema endpoint."""
    
    def test_schema_endpoint_returns_node_types(self, client):
        """Test schema endpoint returns all node types."""
        # Execute
        response = client.get("/api/schema")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert "node_types" in data
        assert isinstance(data["node_types"], dict)
        
        # Verify all expected node types
        expected_node_types = ["Order", "Delivery", "Invoice", "Payment", "Customer", "Product", "Address"]
        for node_type in expected_node_types:
            assert node_type in data["node_types"]
    
    def test_schema_endpoint_returns_relationship_types(self, client):
        """Test schema endpoint returns all relationship types."""
        # Execute
        response = client.get("/api/schema")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert "relationship_types" in data
        assert isinstance(data["relationship_types"], list)
        
        # Verify expected relationship types
        expected_relationships = ["DELIVERED_BY", "BILLED_BY", "PAID_BY", "PURCHASED_BY", "SHIPS_TO", "CONTAINS"]
        for rel_type in expected_relationships:
            assert rel_type in data["relationship_types"]
    
    def test_schema_endpoint_order_properties(self, client):
        """Test schema endpoint returns correct Order properties."""
        # Execute
        response = client.get("/api/schema")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        order_properties = data["node_types"]["Order"]
        
        expected_properties = ["order_id", "customer_id", "order_date", "total_amount", "status"]
        for prop in expected_properties:
            assert prop in order_properties
    
    def test_schema_endpoint_delivery_properties(self, client):
        """Test schema endpoint returns correct Delivery properties."""
        # Execute
        response = client.get("/api/schema")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        delivery_properties = data["node_types"]["Delivery"]
        
        expected_properties = ["delivery_id", "order_id", "delivery_date", "status", "tracking_number"]
        for prop in expected_properties:
            assert prop in delivery_properties
    
    def test_schema_endpoint_customer_properties(self, client):
        """Test schema endpoint returns correct Customer properties."""
        # Execute
        response = client.get("/api/schema")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        customer_properties = data["node_types"]["Customer"]
        
        expected_properties = ["customer_id", "name", "email", "phone", "address_id"]
        for prop in expected_properties:
            assert prop in customer_properties


class TestHealthEndpointIntegration:
    """Integration tests for GET /api/health endpoint."""
    
    def test_health_endpoint_all_services_healthy(self, client, mock_services):
        """Test health endpoint when all services are healthy."""
        # Setup
        mock_services['neo4j'].health_check.return_value = True
        
        with patch.dict('os.environ', {'LLM_PROVIDER': 'groq'}):
            # Execute
            response = client.get("/api/health")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["neo4j_connected"] is True
        assert data["llm_provider"] == "groq"
    
    def test_health_endpoint_neo4j_disconnected(self, client, mock_services):
        """Test health endpoint when Neo4j is disconnected."""
        # Setup
        mock_services['neo4j'].health_check.return_value = False
        
        with patch.dict('os.environ', {'LLM_PROVIDER': 'gemini'}):
            # Execute
            response = client.get("/api/health")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["neo4j_connected"] is False
        assert data["llm_provider"] == "gemini"
    
    def test_health_endpoint_default_llm_provider(self, client, mock_services):
        """Test health endpoint returns default LLM provider."""
        # Setup
        mock_services['neo4j'].health_check.return_value = True
        
        with patch.dict('os.environ', {}, clear=True):
            # Execute
            response = client.get("/api/health")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["llm_provider"] == "groq"  # Default value
    
    def test_health_endpoint_exception_handling(self, client, mock_services):
        """Test health endpoint handles exceptions gracefully."""
        # Setup
        mock_services['neo4j'].health_check.side_effect = Exception("Connection timeout")
        
        # Execute
        response = client.get("/api/health")
        
        # Verify
        assert response.status_code == 500
        error_data = response.json()
        assert "Health check failed" in error_data["detail"]


class TestErrorHandlingIntegration:
    """Integration tests for error handling across endpoints."""
    
    def test_query_endpoint_handles_malformed_json(self, client):
        """Test query endpoint with malformed JSON."""
        # Execute
        response = client.post(
            "/api/query",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Verify: Should return error
        assert response.status_code == 422
    
    def test_graph_endpoint_handles_invalid_limit_type(self, client, mock_services):
        """Test graph endpoint with invalid limit type."""
        # Execute
        response = client.get("/api/graph?limit=invalid")
        
        # Verify: Should return validation error
        assert response.status_code == 422
    
    def test_import_endpoint_handles_empty_filename(self, client, mock_services):
        """Test import endpoint with empty filename."""
        # Execute
        response = client.post(
            "/api/import",
            files={"file": ("", b"data", "text/csv")}
        )
        
        # Verify
        assert response.status_code == 400
        error_data = response.json()
        assert "No filename provided" in error_data["detail"]


class TestStatusCodeIntegration:
    """Integration tests for HTTP status codes."""
    
    def test_successful_query_returns_200(self, client, mock_services):
        """Test successful query returns 200 OK."""
        mock_services['guardrail'].classify_query.return_value = QueryClassification(is_valid=True)
        mock_services['translator'].translate.return_value = TranslationResult(cypher="MATCH (n) RETURN n", success=True)
        mock_services['neo4j'].execute_query.return_value = []
        
        response = client.post("/api/query", json={"query": "test"})
        assert response.status_code == 200
    
    def test_successful_graph_returns_200(self, client, mock_services):
        """Test successful graph request returns 200 OK."""
        mock_services['neo4j'].get_graph_data.return_value = {"nodes": [], "edges": []}
        
        response = client.get("/api/graph")
        assert response.status_code == 200
    
    def test_successful_import_returns_200(self, client, mock_services):
        """Test successful import returns 200 OK."""
        mock_services['import'].import_file.return_value = ImportResult(
            success=True, nodes_created=5, relationships_created=3, errors=[]
        )
        
        response = client.post(
            "/api/import",
            files={"file": ("test.csv", b"data", "text/csv")}
        )
        assert response.status_code == 200
    
    def test_invalid_file_type_returns_400(self, client):
        """Test invalid file type returns 400 Bad Request."""
        response = client.post(
            "/api/import",
            files={"file": ("test.pdf", b"data", "application/pdf")}
        )
        assert response.status_code == 400
    
    def test_missing_required_field_returns_422(self, client):
        """Test missing required field returns 422 Unprocessable Entity."""
        response = client.post("/api/query", json={})
        assert response.status_code == 422
    
    def test_database_error_returns_500(self, client, mock_services):
        """Test database error returns 500 Internal Server Error."""
        mock_services['neo4j'].get_graph_data.side_effect = Exception("DB error")
        
        response = client.get("/api/graph")
        assert response.status_code == 500
