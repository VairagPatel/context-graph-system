"""
Unit tests for DataImportService

Tests cover CSV/JSON parsing, data validation, node creation,
and relationship inference for all 7 entity types.
"""

import pytest
import tempfile
import json
import csv
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from app.services.data_import import DataImportService, ImportResult, ValidationResult, Relationship
from app.services.neo4j_service import Neo4jService


class TestDataImportServiceInitialization:
    """Test DataImportService initialization."""
    
    def test_initialization(self):
        """Test successful initialization with Neo4jService."""
        mock_neo4j = Mock(spec=Neo4jService)
        service = DataImportService(mock_neo4j)
        
        assert service.neo4j_service == mock_neo4j
        assert service._entity_id_map == {}


class TestCSVParsing:
    """Test CSV file parsing functionality."""
    
    @pytest.fixture
    def service(self):
        """Create DataImportService with mock Neo4jService."""
        mock_neo4j = Mock(spec=Neo4jService)
        return DataImportService(mock_neo4j)
    
    def test_parse_csv_orders(self, service):
        """Test parsing orders CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='_orders.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['order_id', 'customer_id', 'order_date', 'total_amount'])
            writer.writeheader()
            writer.writerow({
                'order_id': 'ORD001',
                'customer_id': 'CUST001',
                'order_date': '2024-01-15',
                'total_amount': '150.00'
            })
            temp_path = f.name
        
        try:
            data, entity_type = service._parse_csv(temp_path)
            
            assert entity_type == "Order"
            assert len(data) == 1
            assert data[0]['order_id'] == 'ORD001'
            assert data[0]['customer_id'] == 'CUST001'
        finally:
            Path(temp_path).unlink()
    
    def test_parse_csv_products(self, service):
        """Test parsing products CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='_products.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['product_id', 'name', 'price', 'category'])
            writer.writeheader()
            writer.writerow({
                'product_id': 'PROD001',
                'name': 'Widget',
                'price': '25.99',
                'category': 'Electronics'
            })
            temp_path = f.name
        
        try:
            data, entity_type = service._parse_csv(temp_path)
            
            assert entity_type == "Product"
            assert len(data) == 1
            assert data[0]['product_id'] == 'PROD001'
        finally:
            Path(temp_path).unlink()


class TestJSONParsing:
    """Test JSON file parsing functionality."""
    
    @pytest.fixture
    def service(self):
        """Create DataImportService with mock Neo4jService."""
        mock_neo4j = Mock(spec=Neo4jService)
        return DataImportService(mock_neo4j)
    
    def test_parse_json_with_entity_type(self, service):
        """Test parsing JSON with explicit entity_type field."""
        json_data = {
            "entity_type": "Customer",
            "data": [
                {"customer_id": "CUST001", "name": "John Doe", "email": "john@example.com"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_data, f)
            temp_path = f.name
        
        try:
            data, entity_type = service._parse_json(temp_path)
            
            assert entity_type == "Customer"
            assert len(data) == 1
            assert data[0]['customer_id'] == 'CUST001'
        finally:
            Path(temp_path).unlink()
    
    def test_parse_json_array_with_filename(self, service):
        """Test parsing JSON array inferring type from filename."""
        json_data = [
            {"invoice_id": "INV001", "order_id": "ORD001", "invoice_date": "2024-01-20", "amount": "150.00"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_invoices.json', delete=False) as f:
            json.dump(json_data, f)
            temp_path = f.name
        
        try:
            data, entity_type = service._parse_json(temp_path)
            
            assert entity_type == "Invoice"
            assert len(data) == 1
        finally:
            Path(temp_path).unlink()


class TestEntityTypeInference:
    """Test entity type inference from filenames."""
    
    @pytest.fixture
    def service(self):
        """Create DataImportService with mock Neo4jService."""
        mock_neo4j = Mock(spec=Neo4jService)
        return DataImportService(mock_neo4j)
    
    def test_infer_order(self, service):
        """Test inferring Order entity type."""
        assert service._infer_entity_type("orders") == "Order"
        assert service._infer_entity_type("order_data") == "Order"
    
    def test_infer_delivery(self, service):
        """Test inferring Delivery entity type."""
        assert service._infer_entity_type("deliveries") == "Delivery"
        assert service._infer_entity_type("delivery_info") == "Delivery"
    
    def test_infer_invoice(self, service):
        """Test inferring Invoice entity type."""
        assert service._infer_entity_type("invoices") == "Invoice"
    
    def test_infer_payment(self, service):
        """Test inferring Payment entity type."""
        assert service._infer_entity_type("payments") == "Payment"
    
    def test_infer_customer(self, service):
        """Test inferring Customer entity type."""
        assert service._infer_entity_type("customers") == "Customer"
    
    def test_infer_product(self, service):
        """Test inferring Product entity type."""
        assert service._infer_entity_type("products") == "Product"
    
    def test_infer_address(self, service):
        """Test inferring Address entity type."""
        assert service._infer_entity_type("addresses") == "Address"
    
    def test_infer_unknown(self, service):
        """Test error on unknown entity type."""
        with pytest.raises(ValueError, match="Cannot infer entity type"):
            service._infer_entity_type("unknown_file")


class TestDataValidation:
    """Test data validation functionality."""
    
    @pytest.fixture
    def service(self):
        """Create DataImportService with mock Neo4jService."""
        mock_neo4j = Mock(spec=Neo4jService)
        return DataImportService(mock_neo4j)
    
    def test_validate_order_success(self, service):
        """Test successful validation of Order data."""
        data = [
            {"order_id": "ORD001", "customer_id": "CUST001", "order_date": "2024-01-15", "total_amount": "150.00"}
        ]
        
        result = service._validate_data(data, "Order")
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_order_missing_required_field(self, service):
        """Test validation failure for missing required field."""
        data = [
            {"order_id": "ORD001", "order_date": "2024-01-15"}  # Missing customer_id
        ]
        
        result = service._validate_data(data, "Order")
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "customer_id" in result.errors[0]
    
    def test_validate_product_success(self, service):
        """Test successful validation of Product data."""
        data = [
            {"product_id": "PROD001", "name": "Widget", "price": "25.99"}
        ]
        
        result = service._validate_data(data, "Product")
        
        assert result.is_valid is True
    
    def test_validate_customer_success(self, service):
        """Test successful validation of Customer data."""
        data = [
            {"customer_id": "CUST001", "name": "John Doe"}
        ]
        
        result = service._validate_data(data, "Customer")
        
        assert result.is_valid is True
    
    def test_validate_address_success(self, service):
        """Test successful validation of Address data."""
        data = [
            {"address_id": "ADDR001", "city": "New York", "country": "USA"}
        ]
        
        result = service._validate_data(data, "Address")
        
        assert result.is_valid is True
    
    def test_validate_unknown_entity_type(self, service):
        """Test validation with unknown entity type."""
        data = [{"id": "123"}]
        
        result = service._validate_data(data, "UnknownType")
        
        assert result.is_valid is False
        assert "Unknown entity type" in result.errors[0]


class TestRelationshipInference:
    """Test relationship inference from foreign keys."""
    
    @pytest.fixture
    def service(self):
        """Create DataImportService with mock Neo4jService."""
        mock_neo4j = Mock(spec=Neo4jService)
        service = DataImportService(mock_neo4j)
        
        # Pre-populate entity ID map
        service._entity_id_map = {
            "Order": {"ORD001": "1"},
            "Customer": {"CUST001": "2"},
            "Delivery": {"DEL001": "3"},
            "Invoice": {"INV001": "4"}
        }
        
        return service
    
    def test_infer_order_customer_relationship(self, service):
        """Test inferring PURCHASED_BY relationship from Order to Customer."""
        entities = {
            "Order": [
                {"order_id": "ORD001", "customer_id": "CUST001", "order_date": "2024-01-15"}
            ]
        }
        
        relationships = service._infer_relationships(entities)
        
        # Should create PURCHASED_BY relationship
        assert len(relationships) > 0
        purchased_by_rels = [r for r in relationships if r.rel_type == "PURCHASED_BY"]
        assert len(purchased_by_rels) == 1
        assert purchased_by_rels[0].source_id == "1"  # Order neo4j ID
        assert purchased_by_rels[0].target_id == "2"  # Customer neo4j ID
    
    def test_infer_delivery_order_relationship(self, service):
        """Test inferring DELIVERED_BY relationship (reverse direction)."""
        entities = {
            "Delivery": [
                {"delivery_id": "DEL001", "order_id": "ORD001", "delivery_date": "2024-01-20"}
            ]
        }
        
        relationships = service._infer_relationships(entities)
        
        # Should create DELIVERED_BY relationship (reverse direction)
        assert len(relationships) > 0
        delivered_by_rels = [r for r in relationships if r.rel_type == "DELIVERED_BY"]
        assert len(delivered_by_rels) == 1
    
    def test_infer_no_relationships_missing_target(self, service):
        """Test no relationships created when target entity doesn't exist."""
        entities = {
            "Order": [
                {"order_id": "ORD002", "customer_id": "CUST999", "order_date": "2024-01-15"}
            ]
        }
        
        # ORD002 not in entity_id_map
        relationships = service._infer_relationships(entities)
        
        assert len(relationships) == 0


class TestImportFile:
    """Test complete file import workflow."""
    
    @pytest.fixture
    def service(self):
        """Create DataImportService with mock Neo4jService."""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.create_node.side_effect = lambda label, props: str(hash(props.get('order_id', props.get('product_id', 'default'))))
        mock_neo4j.create_relationship.return_value = "rel_123"
        return DataImportService(mock_neo4j)
    
    def test_import_csv_success(self, service):
        """Test successful CSV import."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='_products.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['product_id', 'name', 'price'])
            writer.writeheader()
            writer.writerow({'product_id': 'PROD001', 'name': 'Widget', 'price': '25.99'})
            writer.writerow({'product_id': 'PROD002', 'name': 'Gadget', 'price': '35.99'})
            temp_path = f.name
        
        try:
            result = service.import_file(temp_path, 'csv')
            
            assert result.success is True
            assert result.nodes_created == 2
            assert len(result.errors) == 0
        finally:
            Path(temp_path).unlink()
    
    def test_import_json_success(self, service):
        """Test successful JSON import."""
        json_data = {
            "entity_type": "Customer",
            "data": [
                {"customer_id": "CUST001", "name": "John Doe"},
                {"customer_id": "CUST002", "name": "Jane Smith"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_data, f)
            temp_path = f.name
        
        try:
            result = service.import_file(temp_path, 'json')
            
            assert result.success is True
            assert result.nodes_created == 2
        finally:
            Path(temp_path).unlink()
    
    def test_import_unsupported_file_type(self, service):
        """Test import with unsupported file type."""
        result = service.import_file("dummy.xml", "xml")
        
        assert result.success is False
        assert "Unsupported file type" in result.errors[0]
    
    def test_import_validation_failure(self, service):
        """Test import with validation errors."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='_orders.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['order_id', 'order_date'])
            writer.writeheader()
            writer.writerow({'order_id': 'ORD001', 'order_date': '2024-01-15'})  # Missing customer_id
            temp_path = f.name
        
        try:
            result = service.import_file(temp_path, 'csv')
            
            assert result.success is False
            assert len(result.errors) > 0
        finally:
            Path(temp_path).unlink()


class TestGetEntityKey:
    """Test entity key extraction."""
    
    @pytest.fixture
    def service(self):
        """Create DataImportService with mock Neo4jService."""
        mock_neo4j = Mock(spec=Neo4jService)
        return DataImportService(mock_neo4j)
    
    def test_get_order_key(self, service):
        """Test extracting Order entity key."""
        entity_data = {"order_id": "ORD001", "customer_id": "CUST001"}
        key = service._get_entity_key("Order", entity_data)
        assert key == "ORD001"
    
    def test_get_product_key(self, service):
        """Test extracting Product entity key."""
        entity_data = {"product_id": "PROD001", "name": "Widget"}
        key = service._get_entity_key("Product", entity_data)
        assert key == "PROD001"
    
    def test_get_customer_key(self, service):
        """Test extracting Customer entity key."""
        entity_data = {"customer_id": "CUST001", "name": "John"}
        key = service._get_entity_key("Customer", entity_data)
        assert key == "CUST001"


class TestValidationAllEntityTypes:
    """Test validation for all 7 entity types."""
    
    @pytest.fixture
    def service(self):
        """Create DataImportService with mock Neo4jService."""
        mock_neo4j = Mock(spec=Neo4jService)
        return DataImportService(mock_neo4j)
    
    def test_validate_delivery_success(self, service):
        """Test successful validation of Delivery data."""
        data = [
            {"delivery_id": "DEL001", "order_id": "ORD001", "delivery_date": "2024-01-20"}
        ]
        
        result = service._validate_data(data, "Delivery")
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_delivery_missing_field(self, service):
        """Test validation failure for Delivery missing required field."""
        data = [
            {"delivery_id": "DEL001", "delivery_date": "2024-01-20"}  # Missing order_id
        ]
        
        result = service._validate_data(data, "Delivery")
        
        assert result.is_valid is False
        assert "order_id" in result.errors[0]
    
    def test_validate_invoice_success(self, service):
        """Test successful validation of Invoice data."""
        data = [
            {"invoice_id": "INV001", "order_id": "ORD001", "invoice_date": "2024-01-25", "amount": "150.00"}
        ]
        
        result = service._validate_data(data, "Invoice")
        
        assert result.is_valid is True
    
    def test_validate_invoice_missing_amount(self, service):
        """Test validation failure for Invoice missing amount."""
        data = [
            {"invoice_id": "INV001", "order_id": "ORD001", "invoice_date": "2024-01-25"}  # Missing amount
        ]
        
        result = service._validate_data(data, "Invoice")
        
        assert result.is_valid is False
        assert "amount" in result.errors[0]
    
    def test_validate_payment_success(self, service):
        """Test successful validation of Payment data."""
        data = [
            {"payment_id": "PAY001", "invoice_id": "INV001", "payment_date": "2024-02-01", "amount": "150.00"}
        ]
        
        result = service._validate_data(data, "Payment")
        
        assert result.is_valid is True
    
    def test_validate_payment_missing_fields(self, service):
        """Test validation failure for Payment missing multiple fields."""
        data = [
            {"payment_id": "PAY001"}  # Missing invoice_id, payment_date, amount
        ]
        
        result = service._validate_data(data, "Payment")
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "invoice_id" in result.errors[0]


class TestRelationshipInferenceComprehensive:
    """Test comprehensive relationship inference for all relationship types."""
    
    @pytest.fixture
    def service(self):
        """Create DataImportService with mock Neo4jService."""
        mock_neo4j = Mock(spec=Neo4jService)
        service = DataImportService(mock_neo4j)
        
        # Pre-populate entity ID map with all entity types
        service._entity_id_map = {
            "Order": {"ORD001": "1", "ORD002": "2"},
            "Customer": {"CUST001": "10"},
            "Address": {"ADDR001": "20"},
            "Delivery": {"DEL001": "30"},
            "Invoice": {"INV001": "40", "INV002": "41"},
            "Payment": {"PAY001": "50"}
        }
        
        return service
    
    def test_infer_ships_to_relationship(self, service):
        """Test inferring SHIPS_TO relationship from Order to Address."""
        entities = {
            "Order": [
                {"order_id": "ORD001", "customer_id": "CUST001", "address_id": "ADDR001", "order_date": "2024-01-15"}
            ]
        }
        
        relationships = service._infer_relationships(entities)
        
        ships_to_rels = [r for r in relationships if r.rel_type == "SHIPS_TO"]
        assert len(ships_to_rels) == 1
        assert ships_to_rels[0].source_id == "1"  # Order neo4j ID
        assert ships_to_rels[0].target_id == "20"  # Address neo4j ID
    
    def test_infer_billed_by_relationship(self, service):
        """Test inferring BILLED_BY relationship from Invoice to Order (reverse)."""
        entities = {
            "Invoice": [
                {"invoice_id": "INV001", "order_id": "ORD001", "invoice_date": "2024-01-25", "amount": "150.00"}
            ]
        }
        
        relationships = service._infer_relationships(entities)
        
        billed_by_rels = [r for r in relationships if r.rel_type == "BILLED_BY"]
        assert len(billed_by_rels) == 1
        # Reverse relationship: Invoice -> Order
        assert billed_by_rels[0].source_id == "40"  # Invoice neo4j ID
        assert billed_by_rels[0].target_id == "1"  # Order neo4j ID
    
    def test_infer_paid_by_relationship(self, service):
        """Test inferring PAID_BY relationship from Payment to Invoice (reverse)."""
        entities = {
            "Payment": [
                {"payment_id": "PAY001", "invoice_id": "INV001", "payment_date": "2024-02-01", "amount": "150.00"}
            ]
        }
        
        relationships = service._infer_relationships(entities)
        
        paid_by_rels = [r for r in relationships if r.rel_type == "PAID_BY"]
        assert len(paid_by_rels) == 1
        assert paid_by_rels[0].source_id == "50"  # Payment neo4j ID
        assert paid_by_rels[0].target_id == "40"  # Invoice neo4j ID
    
    def test_infer_located_at_relationship(self, service):
        """Test inferring LOCATED_AT relationship from Customer to Address."""
        entities = {
            "Customer": [
                {"customer_id": "CUST001", "name": "John Doe", "address_id": "ADDR001"}
            ]
        }
        
        relationships = service._infer_relationships(entities)
        
        located_at_rels = [r for r in relationships if r.rel_type == "LOCATED_AT"]
        assert len(located_at_rels) == 1
        assert located_at_rels[0].source_id == "10"  # Customer neo4j ID
        assert located_at_rels[0].target_id == "20"  # Address neo4j ID
    
    def test_infer_multiple_relationships_same_entity(self, service):
        """Test inferring multiple relationships from a single Order entity."""
        entities = {
            "Order": [
                {
                    "order_id": "ORD001",
                    "customer_id": "CUST001",
                    "address_id": "ADDR001",
                    "order_date": "2024-01-15"
                }
            ]
        }
        
        relationships = service._infer_relationships(entities)
        
        # Should create both PURCHASED_BY and SHIPS_TO
        assert len(relationships) == 2
        rel_types = {r.rel_type for r in relationships}
        assert "PURCHASED_BY" in rel_types
        assert "SHIPS_TO" in rel_types


class TestErrorHandling:
    """Test error handling for various failure scenarios."""
    
    @pytest.fixture
    def service(self):
        """Create DataImportService with mock Neo4jService."""
        mock_neo4j = Mock(spec=Neo4jService)
        return DataImportService(mock_neo4j)
    
    def test_import_file_not_found(self, service):
        """Test import with non-existent file."""
        result = service.import_file("nonexistent_file.csv", "csv")
        
        assert result.success is False
        assert len(result.errors) > 0
        assert result.nodes_created == 0
    
    def test_import_malformed_csv(self, service):
        """Test import with malformed CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='_orders.csv', delete=False) as f:
            # Write invalid CSV (missing closing quote)
            f.write('order_id,customer_id,order_date\n')
            f.write('"ORD001,"CUST001","2024-01-15\n')
            temp_path = f.name
        
        try:
            result = service.import_file(temp_path, 'csv')
            
            # Should handle gracefully
            assert result.success is False or result.nodes_created == 0
        finally:
            Path(temp_path).unlink()
    
    def test_import_malformed_json(self, service):
        """Test import with malformed JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Write invalid JSON
            f.write('{"entity_type": "Order", "data": [')
            temp_path = f.name
        
        try:
            result = service.import_file(temp_path, 'json')
            
            assert result.success is False
            assert len(result.errors) > 0
        finally:
            Path(temp_path).unlink()
    
    def test_import_empty_csv(self, service):
        """Test import with empty CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='_orders.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['order_id', 'customer_id', 'order_date'])
            writer.writeheader()
            # No data rows
            temp_path = f.name
        
        try:
            result = service.import_file(temp_path, 'csv')
            
            assert result.success is False
            assert "No data found" in result.errors[0]
        finally:
            Path(temp_path).unlink()
    
    def test_node_creation_failure(self, service):
        """Test handling of database errors during node creation."""
        service.neo4j_service.create_node = Mock(side_effect=Exception("Database connection failed"))
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_products.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['product_id', 'name', 'price'])
            writer.writeheader()
            writer.writerow({'product_id': 'PROD001', 'name': 'Widget', 'price': '25.99'})
            temp_path = f.name
        
        try:
            result = service.import_file(temp_path, 'csv')
            
            assert result.nodes_created == 0
            assert len(result.errors) > 0
            assert "Failed to create" in result.errors[0]
        finally:
            Path(temp_path).unlink()
    
    def test_relationship_creation_failure(self, service):
        """Test handling of errors during relationship creation."""
        service.neo4j_service.create_node = Mock(return_value="node_123")
        service.neo4j_service.create_relationship = Mock(side_effect=Exception("Relationship creation failed"))
        
        # Pre-populate entity map
        service._entity_id_map = {
            "Customer": {"CUST001": "cust_123"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_orders.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['order_id', 'customer_id', 'order_date'])
            writer.writeheader()
            writer.writerow({'order_id': 'ORD001', 'customer_id': 'CUST001', 'order_date': '2024-01-15'})
            temp_path = f.name
        
        try:
            result = service.import_file(temp_path, 'csv')
            
            # Nodes should be created but relationships fail
            assert result.nodes_created > 0
            assert result.relationships_created == 0
            assert len(result.errors) > 0
        finally:
            Path(temp_path).unlink()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def service(self):
        """Create DataImportService with mock Neo4jService."""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.create_node.side_effect = lambda label, props: f"node_{hash(str(props))}"
        mock_neo4j.create_relationship.return_value = "rel_123"
        return DataImportService(mock_neo4j)
    
    def test_import_duplicate_ids(self, service):
        """Test import with duplicate entity IDs."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='_products.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['product_id', 'name', 'price'])
            writer.writeheader()
            writer.writerow({'product_id': 'PROD001', 'name': 'Widget', 'price': '25.99'})
            writer.writerow({'product_id': 'PROD001', 'name': 'Gadget', 'price': '35.99'})  # Duplicate ID
            temp_path = f.name
        
        try:
            result = service.import_file(temp_path, 'csv')
            
            # Should create both nodes (database should handle uniqueness)
            assert result.nodes_created == 2
        finally:
            Path(temp_path).unlink()
    
    def test_import_missing_optional_fields(self, service):
        """Test import with missing optional fields."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='_orders.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['order_id', 'customer_id', 'order_date', 'total_amount', 'status'])
            writer.writeheader()
            # Missing optional fields: total_amount, status
            writer.writerow({'order_id': 'ORD001', 'customer_id': 'CUST001', 'order_date': '2024-01-15', 'total_amount': '', 'status': ''})
            temp_path = f.name
        
        try:
            result = service.import_file(temp_path, 'csv')
            
            assert result.success is True
            assert result.nodes_created == 1
        finally:
            Path(temp_path).unlink()
    
    def test_import_special_characters_in_data(self, service):
        """Test import with special characters in data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='_customers.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['customer_id', 'name', 'email'])
            writer.writeheader()
            writer.writerow({
                'customer_id': 'CUST001',
                'name': "O'Brien & Sons, Inc.",
                'email': 'test+special@example.com'
            })
            temp_path = f.name
        
        try:
            result = service.import_file(temp_path, 'csv')
            
            assert result.success is True
            assert result.nodes_created == 1
        finally:
            Path(temp_path).unlink()
    
    def test_import_unicode_characters(self, service):
        """Test import with Unicode characters."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='_customers.csv', delete=False, encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['customer_id', 'name'])
            writer.writeheader()
            writer.writerow({
                'customer_id': 'CUST001',
                'name': 'José García 日本語'
            })
            temp_path = f.name
        
        try:
            result = service.import_file(temp_path, 'csv')
            
            assert result.success is True
            assert result.nodes_created == 1
        finally:
            Path(temp_path).unlink()
    
    def test_relationship_with_missing_foreign_key(self, service):
        """Test relationship inference when foreign key references non-existent entity."""
        # Don't pre-populate entity map
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_orders.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['order_id', 'customer_id', 'order_date'])
            writer.writeheader()
            writer.writerow({'order_id': 'ORD001', 'customer_id': 'CUST999', 'order_date': '2024-01-15'})
            temp_path = f.name
        
        try:
            result = service.import_file(temp_path, 'csv')
            
            # Node should be created but no relationships
            assert result.success is True
            assert result.nodes_created == 1
            assert result.relationships_created == 0
        finally:
            Path(temp_path).unlink()
