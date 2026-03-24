"""
Neo4j Service for Graph Database Operations

This service handles all interactions with the Neo4j graph database,
including query execution, node/relationship creation, and health checks.
"""

from typing import Dict, List, Optional, Any
from neo4j import GraphDatabase, Driver, Session, Result
from neo4j.exceptions import ServiceUnavailable, AuthError, Neo4jError
import logging

logger = logging.getLogger(__name__)


class Neo4jService:
    """
    Service class for Neo4j database operations.
    
    Provides methods for executing Cypher queries, creating nodes and relationships,
    fetching graph data for visualization, and health checks.
    """
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize Neo4j service with connection parameters.
        
        Args:
            uri: Neo4j database URI (e.g., "bolt://localhost:7687")
            user: Database username
            password: Database password
        
        Raises:
            AuthError: If authentication fails
            ServiceUnavailable: If database is not reachable
        """
        self.uri = uri
        self.user = user
        self._driver: Optional[Driver] = None
        
        try:
            self._driver = GraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_pool_size=50,
                connection_timeout=30,
                max_transaction_retry_time=30
            )
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j at {uri}")
        except AuthError as e:
            logger.error(f"Authentication failed for Neo4j: {e}")
            raise
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable at {uri}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {e}")
            raise
    
    def close(self):
        """Close the database driver connection."""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j driver connection closed")
    
    def execute_query(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.
        
        Args:
            cypher: Cypher query string
            parameters: Optional query parameters
        
        Returns:
            List of result records as dictionaries
        
        Raises:
            Neo4jError: If query execution fails
            ServiceUnavailable: If database connection is lost
        """
        if not self._driver:
            raise RuntimeError("Neo4j driver not initialized")
        
        parameters = parameters or {}
        
        try:
            with self._driver.session() as session:
                result = session.run(cypher, parameters)
                # Convert result to list of dictionaries
                records = []
                for record in result:
                    record_dict = {}
                    for key in record.keys():
                        value = record[key]
                        # Convert Neo4j types to Python types
                        record_dict[key] = self._serialize_value(value)
                    records.append(record_dict)
                
                logger.info(f"Query executed successfully, returned {len(records)} records")
                return records
        
        except Neo4jError as e:
            logger.error(f"Neo4j query error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            raise
    
    def health_check(self) -> bool:
        """
        Verify database connectivity.
        
        Returns:
            True if database is reachable and responsive, False otherwise
        """
        if not self._driver:
            return False
        
        try:
            self._driver.verify_connectivity()
            # Execute a simple query to verify database is responsive
            with self._driver.session() as session:
                result = session.run("RETURN 1 AS health")
                result.single()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def create_node(self, label: str, properties: Dict[str, Any]) -> str:
        """
        Create a node with specified label and properties.
        
        Args:
            label: Node label (e.g., "Order", "Customer")
            properties: Dictionary of node properties
        
        Returns:
            Node ID (internal Neo4j ID)
        
        Raises:
            Neo4jError: If node creation fails
        """
        if not self._driver:
            raise RuntimeError("Neo4j driver not initialized")
        
        try:
            # Build property string for Cypher query
            cypher = f"CREATE (n:{label} $properties) RETURN id(n) AS node_id"
            
            with self._driver.session() as session:
                result = session.run(cypher, {"properties": properties})
                record = result.single()
                node_id = str(record["node_id"])
                
                logger.info(f"Created node with label '{label}' and ID {node_id}")
                return node_id
        
        except Neo4jError as e:
            logger.error(f"Failed to create node: {e}")
            raise
    
    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a relationship between two nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            rel_type: Relationship type (e.g., "DELIVERED_BY", "PURCHASED_BY")
            properties: Optional relationship properties
        
        Returns:
            Relationship ID (internal Neo4j ID)
        
        Raises:
            Neo4jError: If relationship creation fails
        """
        if not self._driver:
            raise RuntimeError("Neo4j driver not initialized")
        
        properties = properties or {}
        
        try:
            # Use internal IDs to match nodes
            if properties:
                cypher = f"""
                MATCH (source), (target)
                WHERE id(source) = $source_id AND id(target) = $target_id
                CREATE (source)-[r:{rel_type} $properties]->(target)
                RETURN id(r) AS rel_id
                """
            else:
                cypher = f"""
                MATCH (source), (target)
                WHERE id(source) = $source_id AND id(target) = $target_id
                CREATE (source)-[r:{rel_type}]->(target)
                RETURN id(r) AS rel_id
                """
            
            with self._driver.session() as session:
                result = session.run(
                    cypher,
                    {
                        "source_id": int(source_id),
                        "target_id": int(target_id),
                        "properties": properties
                    }
                )
                record = result.single()
                rel_id = str(record["rel_id"])
                
                logger.info(f"Created relationship '{rel_type}' with ID {rel_id}")
                return rel_id
        
        except Neo4jError as e:
            logger.error(f"Failed to create relationship: {e}")
            raise
    
    def get_graph_data(self, limit: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch nodes and edges for graph visualization.
        
        Args:
            limit: Maximum number of nodes to return
        
        Returns:
            Dictionary with 'nodes' and 'edges' lists
        """
        if not self._driver:
            raise RuntimeError("Neo4j driver not initialized")
        
        try:
            with self._driver.session() as session:
                # Fetch nodes
                nodes_query = f"""
                MATCH (n)
                RETURN id(n) AS id, labels(n) AS labels, properties(n) AS properties
                LIMIT {limit}
                """
                nodes_result = session.run(nodes_query)
                nodes = []
                for record in nodes_result:
                    node = {
                        "id": str(record["id"]),
                        "label": record["labels"][0] if record["labels"] else "Unknown",
                        "properties": dict(record["properties"])
                    }
                    nodes.append(node)
                
                # Fetch relationships for the retrieved nodes
                node_ids = [int(node["id"]) for node in nodes]
                if node_ids:
                    edges_query = """
                    MATCH (source)-[r]->(target)
                    WHERE id(source) IN $node_ids AND id(target) IN $node_ids
                    RETURN id(r) AS id, id(source) AS source, id(target) AS target,
                           type(r) AS type, properties(r) AS properties
                    """
                    edges_result = session.run(edges_query, {"node_ids": node_ids})
                    edges = []
                    for record in edges_result:
                        edge = {
                            "id": str(record["id"]),
                            "source": str(record["source"]),
                            "target": str(record["target"]),
                            "type": record["type"],
                            "properties": dict(record["properties"])
                        }
                        edges.append(edge)
                else:
                    edges = []
                
                logger.info(f"Fetched {len(nodes)} nodes and {len(edges)} edges")
                return {"nodes": nodes, "edges": edges}
        
        except Neo4jError as e:
            logger.error(f"Failed to fetch graph data: {e}")
            raise
    
    def _serialize_value(self, value: Any) -> Any:
        """
        Convert Neo4j types to JSON-serializable Python types.
        
        Args:
            value: Value to serialize
        
        Returns:
            JSON-serializable value
        """
        # Handle Neo4j Node objects
        if hasattr(value, 'labels') and hasattr(value, 'items'):
            return {
                "id": str(value.id),
                "labels": list(value.labels),
                "properties": dict(value.items())
            }
        
        # Handle Neo4j Relationship objects
        if hasattr(value, 'type') and hasattr(value, 'start_node'):
            return {
                "id": str(value.id),
                "type": value.type,
                "start_node": str(value.start_node.id),
                "end_node": str(value.end_node.id),
                "properties": dict(value.items())
            }
        
        # Handle Neo4j Path objects
        if hasattr(value, 'nodes') and hasattr(value, 'relationships'):
            return {
                "nodes": [self._serialize_value(node) for node in value.nodes],
                "relationships": [self._serialize_value(rel) for rel in value.relationships]
            }
        
        # Handle lists
        if isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        
        # Handle dictionaries
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        
        # Return primitive types as-is
        return value
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
