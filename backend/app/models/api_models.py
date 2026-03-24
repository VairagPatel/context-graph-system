"""
API data models for the Graph-Based Data Modeling and Query System.

These Pydantic models define the request/response structure for all API endpoints.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for natural language query endpoint."""
    
    query: str = Field(..., description="Natural language query from user")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context tracking")
    include_cypher: Optional[bool] = Field(False, description="Whether to include generated Cypher in response")


class QueryResponse(BaseModel):
    """Response model for query execution results."""
    
    success: bool = Field(..., description="Whether the query executed successfully")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Query result data")
    cypher: Optional[str] = Field(None, description="Generated Cypher query (if requested)")
    error: Optional[str] = Field(None, description="Error message if query failed")
    node_ids: Optional[List[str]] = Field(None, description="Node IDs for visualization highlighting")


class ImportResponse(BaseModel):
    """Response model for data import operations."""
    
    success: bool = Field(..., description="Whether the import succeeded")
    nodes_created: int = Field(..., description="Number of nodes created in the graph")
    relationships_created: int = Field(..., description="Number of relationships created in the graph")
    errors: Optional[List[str]] = Field(None, description="List of errors encountered during import")


class GraphNode(BaseModel):
    """Model representing a graph node for visualization."""
    
    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Node type/label (e.g., Order, Customer)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties as key-value pairs")


class GraphEdge(BaseModel):
    """Model representing a graph edge/relationship for visualization."""
    
    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    type: str = Field(..., description="Relationship type (e.g., DELIVERED_BY, BILLED_BY)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge properties as key-value pairs")


class GraphData(BaseModel):
    """Model containing complete graph data for visualization."""
    
    nodes: List[GraphNode] = Field(default_factory=list, description="List of graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="List of graph edges")


class QueryClassification(BaseModel):
    """Model for guardrail query classification results."""
    
    is_valid: bool = Field(..., description="Whether the query is within the business intelligence domain")
    reason: Optional[str] = Field(None, description="Rejection reason if query is invalid")


class TranslationResult(BaseModel):
    """Model for query translation results from LLM."""
    
    cypher: str = Field(..., description="Generated Cypher query")
    success: bool = Field(..., description="Whether translation succeeded")
    error: Optional[str] = Field(None, description="Error message if translation failed")


class ImportResult(BaseModel):
    """Model for internal data import operation results."""
    
    success: bool = Field(..., description="Whether the import operation succeeded")
    nodes_created: int = Field(..., description="Number of nodes created")
    relationships_created: int = Field(..., description="Number of relationships created")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")
