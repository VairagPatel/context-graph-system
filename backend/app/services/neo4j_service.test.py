"""
Unit tests for Neo4jService

Tests cover connection management, query execution, node/relationship creation,
graph data retrieval, and error handling.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from neo4j.exceptions import ServiceUnavailable, AuthError, Neo4jError
from app.services.neo4j_service import Neo4jService


class TestNeo4jServiceInitialization:
    """Test Neo4jService initialization and connection management."""
    
    def test_successful_initialization(self):
        """Test successful connection to Neo4j database."""
        with patch('app.services.neo4j_service.GraphDatabase') as mock_graph_db:
            mock_driver = Mock()
            mock_driver.verify_connectivity.return_value = None
            mock_graph_db.driver.return_value = mock_driver
            
            service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
            
            mock_graph_db.driver.assert_called_once_with(
                "bolt://localhost:7687",
                auth=("neo4j", "password"),
                max_connection_pool_size=50,
                connection_timeout=30,
                max_transaction_retry_time=30
            )
            mock_driver.verify_connectivity.assert_called_once()
            assert service._driver is not None
    
    def test_initialization_auth_error(self):
        """Test initialization fails with invalid credentials."""
        with patch('app.services.neo4j_service.GraphDatabase') as mock_graph_db:
            mock_driver = Mock()
            mock_driver.verify_connectivity.side_effect = AuthError("Invalid credentials")
            mock_graph_db.driver.return_value = mock_driver
            
            with pytest.raises(AuthError):
                Neo4jService("bolt://localhost:7687", "neo4j", "wrong_password")
    
    def test_initialization_service_unavailable(self):
        """Test initialization fails when database is unreachable."""
        with patch('app.services.neo4j_service.GraphDatabase') as mock_graph_db:
            mock_driver = Mock()
            mock_driver.verify_connectivity.side_effect = ServiceUnavailable("Cannot connect")
            mock_graph_db.driver.return_value = mock_driver
            
            with pytest.raises(ServiceUnavailable):
                Neo4jService("bolt://localhost:7687", "neo4j", "password")
    
    def test_close_connection(self):
        """Test closing database connection."""
        with patch('app.services.neo4j_service.GraphDatabase') as mock_graph_db:
            mock_driver = Mock()
            mock_driver.verify_connectivity.return_value = None
            mock_graph_db.driver.return_value = mock_driver
            
            service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
            service.close()
            
            mock_driver.close.assert_called_once()


class TestExecuteQuery:
    """Test query execution functionality."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock Neo4jService instance."""
        with patch('app.services.neo4j_service.GraphDatabase') as mock_graph_db:
            mock_driver = Mock()
            mock_driver.verify_connectivity.return_value = None
            mock_graph_db.driver.return_value = mock_driver
            
            service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
            yield service, mock_driver
    
    def test_execute_simple_query(self, mock_service):
        """Test executing a simple query with results."""
        service, mock_driver = mock_service
        
        # Mock session and result
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        mock_record = Mock()
        mock_record.keys.return_value = ["name", "count"]
        mock_record.__getitem__.side_effect = lambda key: {"name": "Product A", "count": 10}[key]
        
        mock_result = [mock_record]
        mock_session.run.return_value = mock_result
        
        results = service.execute_query("MATCH (n) RETURN n.name AS name, count(n) AS count")
        
        assert len(results) == 1
        assert results[0]["name"] == "Product A"
        assert results[0]["count"] == 10
    
    def test_execute_query_with_parameters(self, mock_service):
        """Test executing query with parameters."""
        service, mock_driver = mock_service
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        mock_record = Mock()
        mock_record.keys.return_value = ["order_id"]
        mock_record.__getitem__.return_value = "12345"
        
        mock_result = [mock_record]
        mock_session.run.return_value = mock_result
        
        results = service.execute_query(
            "MATCH (o:Order {order_id: $id}) RETURN o.order_id AS order_id",
            {"id": "12345"}
        )
        
        assert len(results) == 1
        assert results[0]["order_id"] == "12345"
        mock_session.run.assert_called_once()
    
    def test_execute_query_empty_results(self, mock_service):
        """Test query returning no results."""
        service, mock_driver = mock_service
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value = []
        
        results = service.execute_query("MATCH (n:NonExistent) RETURN n")
        
        assert results == []
    
    def test_execute_query_neo4j_error(self, mock_service):
        """Test query execution with Neo4j error."""
        service, mock_driver = mock_service
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.side_effect = Neo4jError("Syntax error")
        
        with pytest.raises(Neo4jError):
            service.execute_query("INVALID CYPHER QUERY")
    
    def test_execute_query_without_driver(self):
        """Test query execution fails when driver is not initialized."""
        with patch('app.services.neo4j_service.GraphDatabase'):
            service = Neo4jService.__new__(Neo4jService)
            service._driver = None
            
            with pytest.raises(RuntimeError, match="Neo4j driver not initialized"):
                service.execute_query("MATCH (n) RETURN n")


class TestHealthCheck:
    """Test health check functionality."""
    
    def test_health_check_success(self):
        """Test successful health check."""
        with patch('app.services.neo4j_service.GraphDatabase') as mock_graph_db:
            mock_driver = Mock()
            mock_driver.verify_connectivity.return_value = None
            mock_graph_db.driver.return_value = mock_driver
            
            mock_session = MagicMock()
            mock_driver.session.return_value.__enter__.return_value = mock_session
            mock_session.run.return_value.single.return_value = {"health": 1}
            
            service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
            assert service.health_check() is True
    
    def test_health_check_failure(self):
        """Test health check failure."""
        with patch('app.services.neo4j_service.GraphDatabase') as mock_graph_db:
            mock_driver = Mock()
            mock_driver.verify_connectivity.return_value = None
            mock_graph_db.driver.return_value = mock_driver
            
            service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
            mock_driver.verify_connectivity.side_effect = ServiceUnavailable("Connection lost")
            
            assert service.health_check() is False
    
    def test_health_check_no_driver(self):
        """Test health check with no driver."""
        with patch('app.services.neo4j_service.GraphDatabase'):
            service = Neo4jService.__new__(Neo4jService)
            service._driver = None
            
            assert service.health_check() is False


class TestCreateNode:
    """Test node creation functionality."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock Neo4jService instance."""
        with patch('app.services.neo4j_service.GraphDatabase') as mock_graph_db:
            mock_driver = Mock()
            mock_driver.verify_connectivity.return_value = None
            mock_graph_db.driver.return_value = mock_driver
            
            service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
            yield service, mock_driver
    
    def test_create_node_success(self, mock_service):
        """Test successful node creation."""
        service, mock_driver = mock_service
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        mock_record = Mock()
        mock_record.__getitem__.return_value = 123
        mock_session.run.return_value.single.return_value = mock_record
        
        properties = {"order_id": "12345", "total_amount": 100.0}
        node_id = service.create_node("Order", properties)
        
        assert node_id == "123"
        mock_session.run.assert_called_once()
    
    def test_create_node_with_multiple_properties(self, mock_service):
        """Test creating node with various property types."""
        service, mock_driver = mock_service
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        mock_record = Mock()
        mock_record.__getitem__.return_value = 456
        mock_session.run.return_value.single.return_value = mock_record
        
        properties = {
            "customer_id": "C001",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234"
        }
        node_id = service.create_node("Customer", properties)
        
        assert node_id == "456"
    
    def test_create_node_error(self, mock_service):
        """Test node creation with error."""
        service, mock_driver = mock_service
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.side_effect = Neo4jError("Constraint violation")
        
        with pytest.raises(Neo4jError):
            service.create_node("Order", {"order_id": "12345"})


class TestCreateRelationship:
    """Test relationship creation functionality."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock Neo4jService instance."""
        with patch('app.services.neo4j_service.GraphDatabase') as mock_graph_db:
            mock_driver = Mock()
            mock_driver.verify_connectivity.return_value = None
            mock_graph_db.driver.return_value = mock_driver
            
            service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
            yield service, mock_driver
    
    def test_create_relationship_without_properties(self, mock_service):
        """Test creating relationship without properties."""
        service, mock_driver = mock_service
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        mock_record = Mock()
        mock_record.__getitem__.return_value = 789
        mock_session.run.return_value.single.return_value = mock_record
        
        rel_id = service.create_relationship("123", "456", "DELIVERED_BY")
        
        assert rel_id == "789"
        mock_session.run.assert_called_once()
    
    def test_create_relationship_with_properties(self, mock_service):
        """Test creating relationship with properties."""
        service, mock_driver = mock_service
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        mock_record = Mock()
        mock_record.__getitem__.return_value = 999
        mock_session.run.return_value.single.return_value = mock_record
        
        properties = {"quantity": 5, "unit_price": 20.0}
        rel_id = service.create_relationship("123", "456", "CONTAINS", properties)
        
        assert rel_id == "999"
    
    def test_create_relationship_error(self, mock_service):
        """Test relationship creation with error."""
        service, mock_driver = mock_service
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.side_effect = Neo4jError("Node not found")
        
        with pytest.raises(Neo4jError):
            service.create_relationship("999", "888", "INVALID_REL")


class TestGetGraphData:
    """Test graph data retrieval for visualization."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock Neo4jService instance."""
        with patch('app.services.neo4j_service.GraphDatabase') as mock_graph_db:
            mock_driver = Mock()
            mock_driver.verify_connectivity.return_value = None
            mock_graph_db.driver.return_value = mock_driver
            
            service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
            yield service, mock_driver
    
    def test_get_graph_data_with_nodes_and_edges(self, mock_service):
        """Test fetching graph data with nodes and relationships."""
        service, mock_driver = mock_service
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        # Mock nodes result
        mock_node_record = Mock()
        mock_node_record.__getitem__.side_effect = lambda key: {
            "id": 123,
            "labels": ["Order"],
            "properties": {"order_id": "12345", "total_amount": 100.0}
        }[key]
        
        # Mock edges result
        mock_edge_record = Mock()
        mock_edge_record.__getitem__.side_effect = lambda key: {
            "id": 789,
            "source": 123,
            "target": 456,
            "type": "DELIVERED_BY",
            "properties": {}
        }[key]
        
        mock_session.run.side_effect = [
            [mock_node_record],  # Nodes query
            [mock_edge_record]   # Edges query
        ]
        
        graph_data = service.get_graph_data(limit=100)
        
        assert "nodes" in graph_data
        assert "edges" in graph_data
        assert len(graph_data["nodes"]) == 1
        assert len(graph_data["edges"]) == 1
        assert graph_data["nodes"][0]["label"] == "Order"
        assert graph_data["edges"][0]["type"] == "DELIVERED_BY"
    
    def test_get_graph_data_empty(self, mock_service):
        """Test fetching graph data with no nodes."""
        service, mock_driver = mock_service
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value = []
        
        graph_data = service.get_graph_data(limit=100)
        
        assert graph_data["nodes"] == []
        assert graph_data["edges"] == []
    
    def test_get_graph_data_with_limit(self, mock_service):
        """Test graph data retrieval respects limit parameter."""
        service, mock_driver = mock_service
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value = []
        
        service.get_graph_data(limit=50)
        
        # Verify the limit is used in the query
        call_args = mock_session.run.call_args_list[0]
        assert "LIMIT 50" in call_args[0][0]


class TestContextManager:
    """Test context manager functionality."""
    
    def test_context_manager(self):
        """Test using Neo4jService as context manager."""
        with patch('app.services.neo4j_service.GraphDatabase') as mock_graph_db:
            mock_driver = Mock()
            mock_driver.verify_connectivity.return_value = None
            mock_graph_db.driver.return_value = mock_driver
            
            with Neo4jService("bolt://localhost:7687", "neo4j", "password") as service:
                assert service._driver is not None
            
            mock_driver.close.assert_called_once()


class TestSerializeValue:
    """Test value serialization for Neo4j types."""
    
    @pytest.fixture
    def service(self):
        """Create a Neo4jService instance."""
        with patch('app.services.neo4j_service.GraphDatabase') as mock_graph_db:
            mock_driver = Mock()
            mock_driver.verify_connectivity.return_value = None
            mock_graph_db.driver.return_value = mock_driver
            
            return Neo4jService("bolt://localhost:7687", "neo4j", "password")
    
    def test_serialize_primitive_types(self, service):
        """Test serialization of primitive types."""
        assert service._serialize_value("string") == "string"
        assert service._serialize_value(123) == 123
        assert service._serialize_value(45.67) == 45.67
        assert service._serialize_value(True) is True
        assert service._serialize_value(None) is None
    
    def test_serialize_list(self, service):
        """Test serialization of lists."""
        result = service._serialize_value([1, "two", 3.0])
        assert result == [1, "two", 3.0]
    
    def test_serialize_dict(self, service):
        """Test serialization of dictionaries."""
        result = service._serialize_value({"key": "value", "count": 10})
        assert result == {"key": "value", "count": 10}
    
    def test_serialize_neo4j_node(self, service):
        """Test serialization of Neo4j Node object."""
        mock_node = Mock()
        mock_node.id = 123
        mock_node.labels = ["Order"]
        mock_node.items.return_value = [("order_id", "12345")]
        
        result = service._serialize_value(mock_node)
        
        assert result["id"] == "123"
        assert result["labels"] == ["Order"]
        assert result["properties"] == {"order_id": "12345"}
    
    def test_serialize_neo4j_relationship(self, service):
        """Test serialization of Neo4j Relationship object."""
        mock_rel = Mock()
        mock_rel.id = 789
        mock_rel.type = "DELIVERED_BY"
        mock_rel.start_node.id = 123
        mock_rel.end_node.id = 456
        mock_rel.items.return_value = []
        
        result = service._serialize_value(mock_rel)
        
        assert result["id"] == "789"
        assert result["type"] == "DELIVERED_BY"
        assert result["start_node"] == "123"
        assert result["end_node"] == "456"
