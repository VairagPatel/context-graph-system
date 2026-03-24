"""
SAP Order-to-Cash (O2C) Data Importer

This module handles importing SAP O2C data from JSONL files into Neo4j,
creating appropriate nodes and relationships for the complete O2C flow.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .neo4j_service import Neo4jService

logger = logging.getLogger(__name__)


@dataclass
class ImportStats:
    """Statistics for import operation."""
    entity_type: str
    nodes_created: int
    relationships_created: int
    errors: List[str]


class SapO2CImporter:
    """
    Importer for SAP Order-to-Cash data.
    
    Handles the complete O2C flow:
    Sales Order → Delivery → Billing Document → Journal Entry → Payment
    
    Also imports supporting entities:
    - Business Partners (Customers)
    - Products
    - Plants
    - Addresses
    """
    
    # Entity type configurations
    ENTITY_CONFIGS = {
        "SalesOrder": {
            "id_field": "salesOrder",
            "label": "SalesOrder",
            "required_fields": ["salesOrder"]
        },
        "SalesOrderItem": {
            "id_field": "salesOrderItem",
            "label": "SalesOrderItem",
            "required_fields": ["salesOrder", "salesOrderItem"],
            "composite_id": ["salesOrder", "salesOrderItem"]
        },
        "Delivery": {
            "id_field": "deliveryDocument",
            "label": "Delivery",
            "required_fields": ["deliveryDocument"]
        },
        "DeliveryItem": {
            "id_field": "deliveryDocumentItem",
            "label": "DeliveryItem",
            "required_fields": ["deliveryDocument", "deliveryDocumentItem"],
            "composite_id": ["deliveryDocument", "deliveryDocumentItem"]
        },
        "BillingDocument": {
            "id_field": "billingDocument",
            "label": "BillingDocument",
            "required_fields": ["billingDocument"]
        },
        "BillingDocumentItem": {
            "id_field": "billingDocumentItem",
            "label": "BillingDocumentItem",
            "required_fields": ["billingDocument", "billingDocumentItem"],
            "composite_id": ["billingDocument", "billingDocumentItem"]
        },
        "BusinessPartner": {
            "id_field": "businessPartner",
            "label": "BusinessPartner",
            "required_fields": ["businessPartner"]
        },
        "Product": {
            "id_field": "product",
            "label": "Product",
            "required_fields": ["product"]
        },
        "Plant": {
            "id_field": "plant",
            "label": "Plant",
            "required_fields": ["plant"]
        },
        "Address": {
            "id_field": "addressID",
            "label": "Address",
            "required_fields": ["addressID"]
        },
        "Payment": {
            "id_field": "accountingDocument",
            "label": "Payment",
            "required_fields": ["accountingDocument"],
            "composite_id": ["companyCode", "fiscalYear", "accountingDocument", "accountingDocumentItem"]
        },
        "JournalEntry": {
            "id_field": "accountingDocument",
            "label": "JournalEntry",
            "required_fields": ["accountingDocument"],
            "composite_id": ["companyCode", "fiscalYear", "accountingDocument", "accountingDocumentItem"]
        }
    }
    
    def __init__(self, neo4j_service: Neo4jService):
        """
        Initialize SAP O2C Importer.
        
        Args:
            neo4j_service: Neo4jService instance for database operations
        """
        self.neo4j_service = neo4j_service
        self.entity_map: Dict[str, Dict[str, str]] = {}  # Maps entity_type -> {entity_id -> neo4j_id}
    
    def import_directory(self, data_dir: str) -> List[ImportStats]:
        """
        Import all SAP O2C data from directory.
        
        Args:
            data_dir: Path to sap-o2c-data directory
        
        Returns:
            List of ImportStats for each entity type
        """
        data_path = Path(data_dir)
        if not data_path.exists():
            raise ValueError(f"Data directory not found: {data_dir}")
        
        logger.info(f"Starting SAP O2C data import from {data_dir}")
        
        all_stats = []
        
        # Import order: supporting entities first, then transactional entities
        import_order = [
            # Supporting entities
            ("plants", "Plant"),
            ("products", "Product"),
            ("product_descriptions", "ProductDescription"),
            ("business_partners", "BusinessPartner"),
            ("business_partner_addresses", "Address"),
            
            # Transactional entities (O2C flow)
            ("sales_order_headers", "SalesOrder"),
            ("sales_order_items", "SalesOrderItem"),
            ("outbound_delivery_headers", "Delivery"),
            ("outbound_delivery_items", "DeliveryItem"),
            ("billing_document_headers", "BillingDocument"),
            ("billing_document_items", "BillingDocumentItem"),
            ("journal_entry_items_accounts_receivable", "JournalEntry"),
            ("payments_accounts_receivable", "Payment"),
            
            # Additional entities
            ("product_plants", "ProductPlant"),
            ("customer_company_assignments", "CustomerCompany"),
            ("customer_sales_area_assignments", "CustomerSales"),
        ]
        
        for dir_name, entity_type in import_order:
            entity_dir = data_path / dir_name
            if entity_dir.exists() and entity_dir.is_dir():
                stats = self._import_entity_directory(entity_dir, entity_type)
                all_stats.append(stats)
                logger.info(
                    f"Imported {entity_type}: {stats.nodes_created} nodes, "
                    f"{stats.relationships_created} relationships"
                )
            else:
                logger.warning(f"Directory not found: {entity_dir}")
        
        logger.info("SAP O2C data import completed")
        return all_stats
    
    def _import_entity_directory(self, entity_dir: Path, entity_type: str) -> ImportStats:
        """
        Import all JSONL files from an entity directory.
        
        Args:
            entity_dir: Path to entity directory
            entity_type: Type of entity being imported
        
        Returns:
            ImportStats for this entity type
        """
        nodes_created = 0
        relationships_created = 0
        errors = []
        
        # Find all JSONL files
        jsonl_files = list(entity_dir.glob("*.jsonl"))
        
        if not jsonl_files:
            logger.warning(f"No JSONL files found in {entity_dir}")
            return ImportStats(entity_type, 0, 0, ["No JSONL files found"])
        
        logger.info(f"Processing {len(jsonl_files)} files for {entity_type}")
        
        for jsonl_file in jsonl_files:
            try:
                # Parse JSONL file
                records = self._parse_jsonl(jsonl_file)
                
                # Create nodes
                for record in records:
                    try:
                        node_id = self._create_node(entity_type, record)
                        if node_id:
                            nodes_created += 1
                            
                            # Create relationships
                            rels_created = self._create_relationships(entity_type, record, node_id)
                            relationships_created += rels_created
                    except Exception as e:
                        error_msg = f"Failed to create node for {entity_type}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
            
            except Exception as e:
                error_msg = f"Failed to process file {jsonl_file}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return ImportStats(entity_type, nodes_created, relationships_created, errors)
    
    def _parse_jsonl(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse JSONL file.
        
        Args:
            file_path: Path to JSONL file
        
        Returns:
            List of records
        """
        records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error in {file_path} line {line_num}: {e}")
        
        return records
    
    def _create_node(self, entity_type: str, record: Dict[str, Any]) -> Optional[str]:
        """
        Create a node in Neo4j.
        
        Args:
            entity_type: Type of entity
            record: Entity data
        
        Returns:
            Neo4j node ID or None if creation failed
        """
        config = self.ENTITY_CONFIGS.get(entity_type)
        if not config:
            logger.warning(f"No configuration for entity type: {entity_type}")
            return None
        
        # Get entity ID
        entity_id = self._get_entity_id(entity_type, record)
        if not entity_id:
            logger.warning(f"Could not determine ID for {entity_type}")
            return None
        
        # Create node
        label = config["label"]
        node_id = self.neo4j_service.create_node(label, record)
        
        # Store mapping
        if entity_type not in self.entity_map:
            self.entity_map[entity_type] = {}
        self.entity_map[entity_type][entity_id] = node_id
        
        return node_id
    
    def _get_entity_id(self, entity_type: str, record: Dict[str, Any]) -> Optional[str]:
        """
        Get unique identifier for entity.
        
        Args:
            entity_type: Type of entity
            record: Entity data
        
        Returns:
            Unique identifier string
        """
        config = self.ENTITY_CONFIGS.get(entity_type)
        if not config:
            return None
        
        # Check if composite ID is needed
        if "composite_id" in config:
            id_parts = []
            for field in config["composite_id"]:
                if field in record and record[field]:
                    id_parts.append(str(record[field]))
            return "_".join(id_parts) if id_parts else None
        
        # Single ID field
        id_field = config["id_field"]
        return str(record[id_field]) if id_field in record else None
    
    def _create_relationships(self, entity_type: str, record: Dict[str, Any], source_node_id: str) -> int:
        """
        Create relationships for an entity.
        
        Args:
            entity_type: Type of entity
            record: Entity data
            source_node_id: Neo4j ID of source node
        
        Returns:
            Number of relationships created
        """
        relationships_created = 0
        
        # Define relationship mappings
        relationship_rules = {
            "SalesOrderItem": [
                ("salesOrder", "SalesOrder", "BELONGS_TO_ORDER"),
                ("material", "Product", "CONTAINS_PRODUCT"),
                ("productionPlant", "Plant", "SHIPS_FROM_PLANT"),
            ],
            "DeliveryItem": [
                ("deliveryDocument", "Delivery", "BELONGS_TO_DELIVERY"),
                ("material", "Product", "DELIVERS_PRODUCT"),
                ("referenceSDDocument", "SalesOrder", "FULFILLS_ORDER"),
            ],
            "BillingDocumentItem": [
                ("billingDocument", "BillingDocument", "BELONGS_TO_BILLING"),
                ("material", "Product", "BILLS_PRODUCT"),
                ("salesDocument", "SalesOrder", "BILLS_ORDER"),
            ],
            "BillingDocument": [
                ("soldToParty", "BusinessPartner", "BILLED_TO_CUSTOMER"),
                ("accountingDocument", "JournalEntry", "CREATES_JOURNAL_ENTRY"),
            ],
            "Delivery": [
                ("soldToParty", "BusinessPartner", "DELIVERED_TO_CUSTOMER"),
            ],
            "SalesOrder": [
                ("soldToParty", "BusinessPartner", "SOLD_TO_CUSTOMER"),
            ],
            "Payment": [
                ("customer", "BusinessPartner", "PAID_BY_CUSTOMER"),
                ("clearingAccountingDocument", "JournalEntry", "CLEARS_JOURNAL_ENTRY"),
            ],
            "JournalEntry": [
                ("customer", "BusinessPartner", "RECEIVABLE_FROM_CUSTOMER"),
            ],
        }
        
        rules = relationship_rules.get(entity_type, [])
        
        for field_name, target_entity_type, rel_type in rules:
            if field_name in record and record[field_name]:
                target_id = str(record[field_name])
                
                # Find target node
                if target_entity_type in self.entity_map and target_id in self.entity_map[target_entity_type]:
                    target_node_id = self.entity_map[target_entity_type][target_id]
                    
                    try:
                        self.neo4j_service.create_relationship(
                            source_node_id,
                            target_node_id,
                            rel_type
                        )
                        relationships_created += 1
                    except Exception as e:
                        logger.error(f"Failed to create relationship {rel_type}: {e}")
        
        return relationships_created
