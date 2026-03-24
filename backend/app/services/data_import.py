"""
Data Import Service for Graph Database Population

This service handles importing business data from CSV and JSON files,
validating entity data, and creating nodes and relationships in Neo4j.
"""

from typing import Dict, List, Optional, Any, Set
import csv
import json
import logging
from pathlib import Path
from dataclasses import dataclass
from .neo4j_service import Neo4jService

logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    """Result of data import operation."""
    success: bool
    nodes_created: int
    relationships_created: int
    errors: List[str]


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]


@dataclass
class Relationship:
    """Relationship to be created between entities."""
    source_id: str
    target_id: str
    rel_type: str
    properties: Optional[Dict[str, Any]] = None


class DataImportService:
    """
    Service for importing business data into the graph database.
    
    Supports CSV and JSON file formats for all 7 entity types:
    Order, Delivery, Invoice, Payment, Customer, Product, Address
    """
    
    # Required fields for each entity type
    REQUIRED_FIELDS = {
        "Order": ["order_id", "customer_id", "order_date"],
        "Delivery": ["delivery_id", "order_id", "delivery_date"],
        "Invoice": ["invoice_id", "order_id", "invoice_date", "amount"],
        "Payment": ["payment_id", "invoice_id", "payment_date", "amount"],
        "Customer": ["customer_id", "name"],
        "Product": ["product_id", "name", "price"],
        "Address": ["address_id", "city", "country"]
    }
    
    # Relationship mappings based on foreign keys
    RELATIONSHIP_MAPPINGS = {
        "Order": {
            "customer_id": ("PURCHASED_BY", "Customer"),
            "address_id": ("SHIPS_TO", "Address")
        },
        "Delivery": {
            "order_id": ("DELIVERED_BY", "Order", True)  # True = reverse direction
        },
        "Invoice": {
            "order_id": ("BILLED_BY", "Order", True)
        },
        "Payment": {
            "invoice_id": ("PAID_BY", "Invoice", True)
        },
        "Customer": {
            "address_id": ("LOCATED_AT", "Address")
        }
    }
    
    def __init__(self, neo4j_service: Neo4jService):
        """
        Initialize DataImportService.
        
        Args:
            neo4j_service: Neo4jService instance for database operations
        """
        self.neo4j_service = neo4j_service
        self._entity_id_map: Dict[str, Dict[str, str]] = {}  # Maps entity_type -> {entity_id -> neo4j_id}
    
    def import_file(self, file_path: str, file_type: str) -> ImportResult:
        """
        Import business data from CSV, JSON, or JSONL file.
        
        Args:
            file_path: Path to the data file
            file_type: File format ('csv', 'json', or 'jsonl')
        
        Returns:
            ImportResult with success status, counts, and errors
        """
        errors = []
        nodes_created = 0
        relationships_created = 0
        
        try:
            # Parse file based on type
            if file_type.lower() == 'csv':
                data, entity_type = self._parse_csv(file_path)
            elif file_type.lower() in ['json', 'jsonl']:
                data, entity_type = self._parse_json(file_path)
            else:
                return ImportResult(
                    success=False,
                    nodes_created=0,
                    relationships_created=0,
                    errors=[f"Unsupported file type: {file_type}"]
                )
            
            if not data:
                return ImportResult(
                    success=False,
                    nodes_created=0,
                    relationships_created=0,
                    errors=["No data found in file"]
                )
            
            # Validate data
            validation_result = self._validate_data(data, entity_type)
            if not validation_result.is_valid:
                return ImportResult(
                    success=False,
                    nodes_created=0,
                    relationships_created=0,
                    errors=validation_result.errors
                )
            
            # Create nodes
            logger.info(f"Creating {len(data)} {entity_type} nodes")
            for entity_data in data:
                try:
                    node_id = self.neo4j_service.create_node(entity_type, entity_data)
                    
                    # Store mapping for relationship creation
                    entity_key = self._get_entity_key(entity_type, entity_data)
                    if entity_type not in self._entity_id_map:
                        self._entity_id_map[entity_type] = {}
                    self._entity_id_map[entity_type][entity_key] = node_id
                    
                    nodes_created += 1
                except Exception as e:
                    error_msg = f"Failed to create {entity_type} node: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Infer and create relationships
            logger.info(f"Inferring relationships for {entity_type}")
            relationships = self._infer_relationships({entity_type: data})
            
            for rel in relationships:
                try:
                    self.neo4j_service.create_relationship(
                        rel.source_id,
                        rel.target_id,
                        rel.rel_type,
                        rel.properties
                    )
                    relationships_created += 1
                except Exception as e:
                    error_msg = f"Failed to create relationship {rel.rel_type}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            success = nodes_created > 0
            logger.info(f"Import completed: {nodes_created} nodes, {relationships_created} relationships")
            
            return ImportResult(
                success=success,
                nodes_created=nodes_created,
                relationships_created=relationships_created,
                errors=errors if errors else []
            )
        
        except Exception as e:
            error_msg = f"Import failed: {str(e)}"
            logger.error(error_msg)
            return ImportResult(
                success=False,
                nodes_created=nodes_created,
                relationships_created=relationships_created,
                errors=[error_msg]
            )
    
    def _parse_csv(self, file_path: str) -> tuple[List[Dict[str, Any]], str]:
        """
        Parse CSV file and infer entity type from filename.
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            Tuple of (data list, entity_type)
        """
        path = Path(file_path)
        filename = path.stem.lower()
        
        # Infer entity type from filename
        entity_type = self._infer_entity_type(filename)
        
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Remove empty values
                cleaned_row = {k: v for k, v in row.items() if v}
                data.append(cleaned_row)
        
        logger.info(f"Parsed {len(data)} records from CSV file as {entity_type}")
        return data, entity_type
    
    def _parse_json(self, file_path: str) -> tuple[List[Dict[str, Any]], str]:
        """
        Parse JSON or JSONL file and extract entity type.
        
        Args:
            file_path: Path to JSON or JSONL file
        
        Returns:
            Tuple of (data list, entity_type)
        """
        path = Path(file_path)
        
        # Check if it's a JSONL file (JSON Lines format)
        if file_path.endswith('.jsonl'):
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:  # Skip empty lines
                        data.append(json.loads(line))
            
            # Infer entity type from filename or parent directory
            filename = path.stem.lower()
            parent_dir = path.parent.name.lower()
            entity_type = self._infer_entity_type(parent_dir if parent_dir != 'sap-o2c-data' else filename)
            
            logger.info(f"Parsed {len(data)} records from JSONL file as {entity_type}")
            return data, entity_type
        
        # Regular JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # JSON should have format: {"entity_type": "Order", "data": [...]}
        # or just be an array of objects with filename indicating type
        if isinstance(json_data, dict) and "entity_type" in json_data:
            entity_type = json_data["entity_type"]
            data = json_data.get("data", [])
        elif isinstance(json_data, list):
            filename = path.stem.lower()
            entity_type = self._infer_entity_type(filename)
            data = json_data
        else:
            raise ValueError("Invalid JSON format")
        
        logger.info(f"Parsed {len(data)} records from JSON file as {entity_type}")
        return data, entity_type
    
    def _infer_entity_type(self, filename: str) -> str:
        """
        Infer entity type from filename.
        
        Args:
            filename: Filename (without extension) or directory name
        
        Returns:
            Entity type name
        """
        filename_lower = filename.lower()
        
        # SAP O2C entity mappings
        if "sales_order" in filename_lower:
            return "SalesOrder"
        elif "outbound_delivery" in filename_lower:
            return "Delivery"
        elif "billing_document" in filename_lower:
            return "BillingDocument"
        elif "payment" in filename_lower or "accounts_receivable" in filename_lower:
            return "Payment"
        elif "business_partner" in filename_lower and "address" not in filename_lower:
            return "BusinessPartner"
        elif "business_partner_address" in filename_lower:
            return "Address"
        elif "product" in filename_lower and "plant" not in filename_lower and "storage" not in filename_lower and "description" not in filename_lower:
            return "Product"
        elif "product_description" in filename_lower:
            return "ProductDescription"
        elif "product_plant" in filename_lower:
            return "ProductPlant"
        elif "product_storage" in filename_lower:
            return "ProductStorage"
        elif "plant" in filename_lower and "product" not in filename_lower:
            return "Plant"
        elif "journal_entry" in filename_lower:
            return "JournalEntry"
        elif "customer_company" in filename_lower:
            return "CustomerCompany"
        elif "customer_sales" in filename_lower:
            return "CustomerSales"
        # Legacy entity mappings
        elif "order" in filename_lower:
            return "Order"
        elif "deliver" in filename_lower:
            return "Delivery"
        elif "invoice" in filename_lower:
            return "Invoice"
        elif "customer" in filename_lower:
            return "Customer"
        elif "address" in filename_lower:
            return "Address"
        else:
            raise ValueError(f"Cannot infer entity type from filename: {filename}")
    
    def _validate_data(self, data: List[Dict[str, Any]], entity_type: str) -> ValidationResult:
        """
        Validate required fields for entity type.
        
        Args:
            data: List of entity dictionaries
            entity_type: Type of entity being validated
        
        Returns:
            ValidationResult with validation status and errors
        """
        errors = []
        
        if entity_type not in self.REQUIRED_FIELDS:
            errors.append(f"Unknown entity type: {entity_type}")
            return ValidationResult(is_valid=False, errors=errors)
        
        required_fields = self.REQUIRED_FIELDS[entity_type]
        
        for idx, entity in enumerate(data):
            missing_fields = [field for field in required_fields if field not in entity or not entity[field]]
            
            if missing_fields:
                errors.append(
                    f"Record {idx + 1}: Missing required fields: {', '.join(missing_fields)}"
                )
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info(f"Validation passed for {len(data)} {entity_type} records")
        else:
            logger.warning(f"Validation failed with {len(errors)} errors")
        
        return ValidationResult(is_valid=is_valid, errors=errors)
    
    def _infer_relationships(self, entities: Dict[str, List[Dict[str, Any]]]) -> List[Relationship]:
        """
        Infer relationships from foreign key references.
        
        Args:
            entities: Dictionary mapping entity_type to list of entities
        
        Returns:
            List of Relationship objects to create
        """
        relationships = []
        
        for entity_type, entity_list in entities.items():
            if entity_type not in self.RELATIONSHIP_MAPPINGS:
                continue
            
            mappings = self.RELATIONSHIP_MAPPINGS[entity_type]
            
            for entity_data in entity_list:
                source_key = self._get_entity_key(entity_type, entity_data)
                
                if entity_type not in self._entity_id_map or source_key not in self._entity_id_map[entity_type]:
                    continue
                
                source_neo4j_id = self._entity_id_map[entity_type][source_key]
                
                # Check each foreign key field
                for fk_field, mapping_info in mappings.items():
                    if fk_field not in entity_data or not entity_data[fk_field]:
                        continue
                    
                    # Unpack mapping info
                    if len(mapping_info) == 3:
                        rel_type, target_entity_type, reverse = mapping_info
                    else:
                        rel_type, target_entity_type = mapping_info
                        reverse = False
                    
                    # Find target entity
                    target_key = entity_data[fk_field]
                    
                    if target_entity_type not in self._entity_id_map:
                        continue
                    
                    if target_key not in self._entity_id_map[target_entity_type]:
                        continue
                    
                    target_neo4j_id = self._entity_id_map[target_entity_type][target_key]
                    
                    # Create relationship (handle direction)
                    if reverse:
                        # Relationship goes from target to source
                        relationships.append(Relationship(
                            source_id=source_neo4j_id,
                            target_id=target_neo4j_id,
                            rel_type=rel_type
                        ))
                    else:
                        # Relationship goes from source to target
                        relationships.append(Relationship(
                            source_id=source_neo4j_id,
                            target_id=target_neo4j_id,
                            rel_type=rel_type
                        ))
        
        logger.info(f"Inferred {len(relationships)} relationships")
        return relationships
    
    def _get_entity_key(self, entity_type: str, entity_data: Dict[str, Any]) -> str:
        """
        Get the unique identifier for an entity.
        
        Args:
            entity_type: Type of entity
            entity_data: Entity data dictionary
        
        Returns:
            Unique identifier string
        """
        # Map entity type to its ID field
        id_field_map = {
            "Order": "order_id",
            "Delivery": "delivery_id",
            "Invoice": "invoice_id",
            "Payment": "payment_id",
            "Customer": "customer_id",
            "Product": "product_id",
            "Address": "address_id"
        }
        
        id_field = id_field_map.get(entity_type)
        if not id_field or id_field not in entity_data:
            raise ValueError(f"Cannot find ID field for {entity_type}")
        
        return str(entity_data[id_field])
