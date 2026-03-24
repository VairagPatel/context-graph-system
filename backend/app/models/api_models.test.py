"""
Unit tests for API data models.
"""

import pytest
from app.models.api_models import (
    QueryRequest,
    QueryResponse,
    ImportResponse,
    GraphNode,
    GraphEdge,
    GraphData,
    QueryClassification,
    TranslationResult,
    ImportResult,
)


def test_query_request_minimal():
    """Test QueryRequest with minimal required fields."""
    request = QueryRequest(query="Show me all orders")
    assert request.query == "Show me all orders"
    assert request.conversation_id is None
    assert request.include_cypher is False


def test_query_request_full():
    """Test QueryRequest with all fields."""
    request = QueryRequest(
        query="Show me all orders",
        conversation_id="conv-123",
        include_cypher=True
    )
    assert request.query == "Show me all orders"
    assert request.conversation_id == "conv-123"
    assert request.include_cypher is True


def test_query_response_success():
    """Test QueryResponse for successful query."""
    response = QueryResponse(
        success=True,
        data=[{"order_id": "123", "total": 100.0}],
        cypher="MATCH (o:Order) RETURN o",
        node_ids=["node-1", "node-2"]
    )
    assert response.success is True
    assert len(response.data) == 1
    assert response.cypher is not None
    assert len(response.node_ids) == 2


def test_query_response_error():
    """Test QueryResponse for failed query."""
    response = QueryResponse(
        success=False,
        data=[],
        error="Query translation failed"
    )
    assert response.success is False
    assert len(response.data) == 0
    assert response.error == "Query translation failed"


def test_import_response():
    """Test ImportResponse model."""
    response = ImportResponse(
        success=True,
        nodes_created=100,
        relationships_created=250,
        errors=None
    )
    assert response.success is True
    assert response.nodes_created == 100
    assert response.relationships_created == 250
    assert response.errors is None


def test_graph_node():
    """Test GraphNode model."""
    node = GraphNode(
        id="order-123",
        label="Order",
        properties={"order_id": "123", "total_amount": 100.0}
    )
    assert node.id == "order-123"
    assert node.label == "Order"
    assert node.properties["order_id"] == "123"


def test_graph_edge():
    """Test GraphEdge model."""
    edge = GraphEdge(
        id="edge-1",
        source="order-123",
        target="delivery-456",
        type="DELIVERED_BY",
        properties={}
    )
    assert edge.id == "edge-1"
    assert edge.source == "order-123"
    assert edge.target == "delivery-456"
    assert edge.type == "DELIVERED_BY"


def test_graph_data():
    """Test GraphData model with nodes and edges."""
    node1 = GraphNode(id="n1", label="Order", properties={})
    node2 = GraphNode(id="n2", label="Delivery", properties={})
    edge = GraphEdge(id="e1", source="n1", target="n2", type="DELIVERED_BY", properties={})
    
    graph_data = GraphData(nodes=[node1, node2], edges=[edge])
    assert len(graph_data.nodes) == 2
    assert len(graph_data.edges) == 1


def test_query_classification_valid():
    """Test QueryClassification for valid query."""
    classification = QueryClassification(is_valid=True, reason=None)
    assert classification.is_valid is True
    assert classification.reason is None


def test_query_classification_invalid():
    """Test QueryClassification for invalid query."""
    classification = QueryClassification(
        is_valid=False,
        reason="Query is outside business intelligence domain"
    )
    assert classification.is_valid is False
    assert classification.reason is not None


def test_translation_result_success():
    """Test TranslationResult for successful translation."""
    result = TranslationResult(
        cypher="MATCH (o:Order) RETURN o LIMIT 10",
        success=True,
        error=None
    )
    assert result.success is True
    assert result.cypher.startswith("MATCH")
    assert result.error is None


def test_translation_result_failure():
    """Test TranslationResult for failed translation."""
    result = TranslationResult(
        cypher="",
        success=False,
        error="LLM API timeout"
    )
    assert result.success is False
    assert result.error == "LLM API timeout"


def test_import_result():
    """Test ImportResult model."""
    result = ImportResult(
        success=True,
        nodes_created=50,
        relationships_created=120,
        errors=[]
    )
    assert result.success is True
    assert result.nodes_created == 50
    assert result.relationships_created == 120
    assert len(result.errors) == 0


def test_import_result_with_errors():
    """Test ImportResult with validation errors."""
    result = ImportResult(
        success=False,
        nodes_created=0,
        relationships_created=0,
        errors=["Missing required field: order_id", "Invalid date format"]
    )
    assert result.success is False
    assert len(result.errors) == 2
