"""
Main FastAPI Application

This module serves as the entry point for the Graph-Based Data Modeling and Query System.
It initializes all services, configures middleware, and defines API endpoints.
"""

import logging
import os
from typing import Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

from app.services.neo4j_service import Neo4jService
from app.services.guardrails import GuardrailSystem
from app.services.query_translator import QueryTranslator, GraphSchema
from app.services.data_import import DataImportService
from app.models.api_models import (
    QueryRequest,
    QueryResponse,
    ImportResponse,
    GraphData,
    GraphNode,
    GraphEdge
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instances
neo4j_service: Optional[Neo4jService] = None
guardrail_system: Optional[GuardrailSystem] = None
query_translator: Optional[QueryTranslator] = None
data_import_service: Optional[DataImportService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    logger.info("Starting Graph Query System API")
    
    global neo4j_service, guardrail_system, query_translator, data_import_service
    
    # Load environment variables
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    llm_provider = os.getenv("LLM_PROVIDER", "groq")
    llm_api_key = os.getenv("LLM_API_KEY", "")
    
    # Initialize services
    try:
        # Initialize Neo4j service
        neo4j_service = Neo4jService(neo4j_uri, neo4j_user, neo4j_password)
        logger.info("Neo4j service initialized")
        
        # Initialize guardrail system
        guardrail_system = GuardrailSystem()
        logger.info("Guardrail system initialized")
        
        # Define graph schema for query translator
        schema = GraphSchema(
            node_types={
                # SAP O2C Core Entities
                "SalesOrder": ["salesOrder", "salesOrderType", "soldToParty", "creationDate", "totalNetAmount", "transactionCurrency"],
                "SalesOrderItem": ["salesOrder", "salesOrderItem", "material", "requestedQuantity", "netAmount", "productionPlant"],
                "Delivery": ["deliveryDocument", "creationDate", "shippingPoint", "overallGoodsMovementStatus", "soldToParty"],
                "DeliveryItem": ["deliveryDocument", "deliveryDocumentItem", "material", "actualDeliveryQuantity", "referenceSDDocument"],
                "BillingDocument": ["billingDocument", "billingDocumentType", "billingDocumentDate", "totalNetAmount", "soldToParty", "accountingDocument"],
                "BillingDocumentItem": ["billingDocument", "billingDocumentItem", "material", "billingQuantity", "netAmount", "salesDocument"],
                "JournalEntry": ["companyCode", "fiscalYear", "accountingDocument", "accountingDocumentItem", "postingDate", "amountInTransactionCurrency", "customer"],
                "Payment": ["companyCode", "fiscalYear", "accountingDocument", "clearingDate", "amountInTransactionCurrency", "customer", "clearingAccountingDocument"],
                
                # SAP Supporting Entities
                "BusinessPartner": ["businessPartner", "customer", "businessPartnerFullName", "businessPartnerCategory", "businessPartnerIsBlocked"],
                "Product": ["product", "productType", "productGroup", "baseUnit", "grossWeight", "netWeight"],
                "ProductDescription": ["product", "language", "productDescription"],
                "Plant": ["plant", "plantName", "plantCustomer"],
                "Address": ["addressID", "streetName", "cityName", "postalCode", "country", "region"],
                
                # Legacy Entities (for backward compatibility)
                "Order": ["order_id", "customer_id", "order_date", "total_amount", "status"],
                "Invoice": ["invoice_id", "order_id", "invoice_date", "amount", "status"],
                "Customer": ["customer_id", "name", "email", "phone", "address_id"],
            },
            relationship_types=[
                # SAP O2C Flow Relationships
                "BELONGS_TO_ORDER", "BELONGS_TO_DELIVERY", "BELONGS_TO_BILLING",
                "CONTAINS_PRODUCT", "DELIVERS_PRODUCT", "BILLS_PRODUCT",
                "FULFILLS_ORDER", "BILLS_ORDER", "CREATES_JOURNAL_ENTRY",
                "BILLED_TO_CUSTOMER", "DELIVERED_TO_CUSTOMER", "SOLD_TO_CUSTOMER",
                "PAID_BY_CUSTOMER", "CLEARS_JOURNAL_ENTRY", "RECEIVABLE_FROM_CUSTOMER",
                "SHIPS_FROM_PLANT",
                
                # Legacy Relationships
                "DELIVERED_BY", "BILLED_BY", "PAID_BY", "PURCHASED_BY",
                "SHIPS_TO", "CONTAINS", "INCLUDES_PRODUCT", "LOCATED_AT"
            ]
        )
        
        # Initialize query translator
        query_translator = QueryTranslator(llm_provider, llm_api_key, schema)
        logger.info(f"Query translator initialized with provider: {llm_provider}")
        
        # Initialize data import service
        data_import_service = DataImportService(neo4j_service)
        logger.info("Data import service initialized")
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Graph Query System API")
    if neo4j_service:
        neo4j_service.close()
        logger.info("Neo4j connection closed")


# Initialize FastAPI app
app = FastAPI(
    title="Graph Query System API",
    description="API for graph-based data modeling and natural language querying",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Endpoints

@app.post("/api/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query_endpoint(request: QueryRequest):
    """
    Process natural language query and return results.
    
    Args:
        request: QueryRequest containing natural language query
    
    Returns:
        QueryResponse with query results or error
    """
    try:
        logger.info(f"Received query: {request.query}")
        
        # Validate query with guardrails
        classification = guardrail_system.classify_query(request.query)
        
        if not classification.is_valid:
            logger.warning(f"Query rejected by guardrails: {classification.reason}")
            return QueryResponse(
                success=False,
                data=[],
                error=classification.reason
            )
        
        # Translate natural language to Cypher
        translation_result = query_translator.translate(request.query)
        
        if not translation_result.success:
            logger.error(f"Translation failed: {translation_result.error}")
            return QueryResponse(
                success=False,
                data=[],
                error=f"Failed to translate query: {translation_result.error}"
            )
        
        logger.info(f"Generated Cypher: {translation_result.cypher}")
        
        # Execute Cypher query
        results = neo4j_service.execute_query(translation_result.cypher)
        
        # Build response
        response = QueryResponse(
            success=True,
            data=results,
            cypher=translation_result.cypher if request.include_cypher else None
        )
        
        logger.info(f"Query executed successfully, returned {len(results)} results")
        return response
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        return QueryResponse(
            success=False,
            data=[],
            error=f"Query execution failed: {str(e)}"
        )


@app.get("/api/graph", response_model=GraphData, status_code=status.HTTP_200_OK)
async def get_graph(limit: int = 100):
    """
    Retrieve graph data for visualization.
    
    Args:
        limit: Maximum number of nodes to return (default: 100)
    
    Returns:
        GraphData containing nodes and edges
    """
    try:
        logger.info(f"Fetching graph data with limit: {limit}")
        
        # Get graph data from Neo4j
        graph_data = neo4j_service.get_graph_data(limit)
        
        # Convert to API models
        nodes = [
            GraphNode(
                id=node["id"],
                label=node["label"],
                properties=node["properties"]
            )
            for node in graph_data["nodes"]
        ]
        
        edges = [
            GraphEdge(
                id=edge["id"],
                source=edge["source"],
                target=edge["target"],
                type=edge["type"],
                properties=edge["properties"]
            )
            for edge in graph_data["edges"]
        ]
        
        response = GraphData(nodes=nodes, edges=edges)
        logger.info(f"Returning {len(nodes)} nodes and {len(edges)} edges")
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to fetch graph data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch graph data: {str(e)}"
        )


@app.post("/api/import", response_model=ImportResponse, status_code=status.HTTP_200_OK)
async def import_data(file: UploadFile = File(...)):
    """
    Import business data from CSV or JSON file.
    
    Args:
        file: Uploaded file (CSV or JSON format)
    
    Returns:
        ImportResponse with import statistics
    """
    try:
        logger.info(f"Received file upload: {file.filename}")
        
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )
        
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["csv", "json", "jsonl"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV, JSON, and JSONL files are supported"
            )
        
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Import data
        import_result = data_import_service.import_file(temp_file_path, file_extension)
        
        # Clean up temporary file
        import os
        os.unlink(temp_file_path)
        
        # Build response
        response = ImportResponse(
            success=import_result.success,
            nodes_created=import_result.nodes_created,
            relationships_created=import_result.relationships_created,
            errors=import_result.errors if import_result.errors else None
        )
        
        logger.info(
            f"Import completed: {import_result.nodes_created} nodes, "
            f"{import_result.relationships_created} relationships"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


class SchemaResponse(BaseModel):
    """Response model for schema endpoint."""
    node_types: dict
    relationship_types: list


@app.get("/api/schema", response_model=SchemaResponse, status_code=status.HTTP_200_OK)
async def get_schema():
    """
    Retrieve graph schema definition.
    
    Returns:
        SchemaResponse with node types and relationship types
    """
    try:
        logger.info("Fetching graph schema")
        
        schema = {
            "node_types": {
                # SAP O2C Core Entities
                "SalesOrder": ["salesOrder", "salesOrderType", "soldToParty", "creationDate", "totalNetAmount", "transactionCurrency"],
                "SalesOrderItem": ["salesOrder", "salesOrderItem", "material", "requestedQuantity", "netAmount", "productionPlant"],
                "Delivery": ["deliveryDocument", "creationDate", "shippingPoint", "overallGoodsMovementStatus", "soldToParty"],
                "DeliveryItem": ["deliveryDocument", "deliveryDocumentItem", "material", "actualDeliveryQuantity", "referenceSDDocument"],
                "BillingDocument": ["billingDocument", "billingDocumentType", "billingDocumentDate", "totalNetAmount", "soldToParty", "accountingDocument"],
                "BillingDocumentItem": ["billingDocument", "billingDocumentItem", "material", "billingQuantity", "netAmount", "salesDocument"],
                "JournalEntry": ["companyCode", "fiscalYear", "accountingDocument", "accountingDocumentItem", "postingDate", "amountInTransactionCurrency", "customer"],
                "Payment": ["companyCode", "fiscalYear", "accountingDocument", "clearingDate", "amountInTransactionCurrency", "customer", "clearingAccountingDocument"],
                "BusinessPartner": ["businessPartner", "customer", "businessPartnerFullName", "businessPartnerCategory", "businessPartnerIsBlocked"],
                "Product": ["product", "productType", "productGroup", "baseUnit", "grossWeight", "netWeight"],
                "Plant": ["plant", "plantName", "plantCustomer"],
                "Address": ["addressID", "streetName", "cityName", "postalCode", "country", "region"],
            },
            "relationship_types": [
                "BELONGS_TO_ORDER", "BELONGS_TO_DELIVERY", "BELONGS_TO_BILLING",
                "CONTAINS_PRODUCT", "DELIVERS_PRODUCT", "BILLS_PRODUCT",
                "FULFILLS_ORDER", "BILLS_ORDER", "CREATES_JOURNAL_ENTRY",
                "BILLED_TO_CUSTOMER", "DELIVERED_TO_CUSTOMER", "SOLD_TO_CUSTOMER",
                "PAID_BY_CUSTOMER", "CLEARS_JOURNAL_ENTRY", "RECEIVABLE_FROM_CUSTOMER",
                "SHIPS_FROM_PLANT"
            ]
        }
        
        return SchemaResponse(**schema)
        
    except Exception as e:
        logger.error(f"Failed to fetch schema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch schema: {str(e)}"
        )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    neo4j_connected: bool
    llm_provider: str


@app.get("/api/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Check service health and connectivity.
    
    Returns:
        HealthResponse with service status
    """
    try:
        # Check Neo4j connectivity
        neo4j_connected = neo4j_service.health_check() if neo4j_service else False
        
        # Get LLM provider
        llm_provider = os.getenv("LLM_PROVIDER", "groq")
        
        # Determine overall status
        overall_status = "healthy" if neo4j_connected else "degraded"
        
        logger.info(f"Health check: {overall_status}, Neo4j: {neo4j_connected}")
        
        return HealthResponse(
            status=overall_status,
            neo4j_connected=neo4j_connected,
            llm_provider=llm_provider
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(app, host=host, port=port)
