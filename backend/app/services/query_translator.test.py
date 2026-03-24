"""
Unit tests for QueryTranslator service.

Tests cover initialization, translation logic, prompt building,
Cypher validation, and both Groq and Gemini API interactions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.app.services.query_translator import (
    QueryTranslator,
    TranslationResult,
    GraphSchema
)


# Test fixtures
@pytest.fixture
def sample_schema():
    """Sample graph schema for testing."""
    return GraphSchema(
        node_types={
            "Order": ["order_id", "customer_id", "order_date", "total_amount", "status"],
            "Delivery": ["delivery_id", "order_id", "delivery_date", "status", "tracking_number"],
            "Invoice": ["invoice_id", "order_id", "invoice_date", "amount", "status"],
            "Payment": ["payment_id", "invoice_id", "payment_date", "amount", "payment_method"],
            "Customer": ["customer_id", "name", "email", "phone", "address_id"],
            "Product": ["product_id", "name", "category", "price", "sku"],
            "Address": ["address_id", "street", "city", "state", "postal_code", "country"]
        },
        relationship_types=[
            "DELIVERED_BY",
            "BILLED_BY",
            "PAID_BY",
            "PURCHASED_BY",
            "SHIPS_TO",
            "CONTAINS",
            "INCLUDES_PRODUCT"
        ]
    )


@pytest.fixture
def groq_translator(sample_schema):
    """QueryTranslator instance configured for Groq."""
    return QueryTranslator(
        llm_provider="groq",
        api_key="test_groq_key",
        schema=sample_schema
    )


@pytest.fixture
def gemini_translator(sample_schema):
    """QueryTranslator instance configured for Gemini."""
    return QueryTranslator(
        llm_provider="gemini",
        api_key="test_gemini_key",
        schema=sample_schema
    )


class TestQueryTranslatorInit:
    """Tests for QueryTranslator initialization."""
    
    def test_init_with_groq(self, sample_schema):
        """Test initialization with Groq provider."""
        translator = QueryTranslator("groq", "test_key", sample_schema)
        assert translator.llm_provider == "groq"
        assert translator.api_key == "test_key"
        assert translator.schema == sample_schema
    
    def test_init_with_gemini(self, sample_schema):
        """Test initialization with Gemini provider."""
        translator = QueryTranslator("gemini", "test_key", sample_schema)
        assert translator.llm_provider == "gemini"
        assert translator.api_key == "test_key"
    
    def test_init_with_invalid_provider(self, sample_schema):
        """Test initialization with invalid provider raises ValueError."""
        with pytest.raises(ValueError, match="llm_provider must be 'groq' or 'gemini'"):
            QueryTranslator("invalid_provider", "test_key", sample_schema)
    
    def test_init_case_insensitive(self, sample_schema):
        """Test provider name is case-insensitive."""
        translator1 = QueryTranslator("GROQ", "test_key", sample_schema)
        translator2 = QueryTranslator("Gemini", "test_key", sample_schema)
        assert translator1.llm_provider == "groq"
        assert translator2.llm_provider == "gemini"


class TestBuildPrompt:
    """Tests for _build_prompt method."""
    
    def test_prompt_includes_schema(self, groq_translator):
        """Test that prompt includes schema information."""
        prompt = groq_translator._build_prompt("test query")
        assert "SCHEMA:" in prompt
        assert "Order(" in prompt
        assert "Delivery(" in prompt
        assert "DELIVERED_BY" in prompt
        assert "BILLED_BY" in prompt
    
    def test_prompt_includes_examples(self, groq_translator):
        """Test that prompt includes few-shot examples."""
        prompt = groq_translator._build_prompt("test query")
        assert "EXAMPLES:" in prompt
        assert "Show me the top 10 products" in prompt
        assert "Find orders that have been delivered but not invoiced" in prompt
        assert "Trace the complete flow" in prompt
    
    def test_prompt_includes_user_query(self, groq_translator):
        """Test that prompt includes the user's query."""
        user_query = "What are the most popular products?"
        prompt = groq_translator._build_prompt(user_query)
        assert user_query in prompt
        assert "USER QUERY:" in prompt
    
    def test_prompt_includes_instructions(self, groq_translator):
        """Test that prompt includes generation instructions."""
        prompt = groq_translator._build_prompt("test query")
        assert "INSTRUCTIONS:" in prompt
        assert "LIMIT 20" in prompt
        assert "OPTIONAL MATCH" in prompt


class TestValidateCypher:
    """Tests for _validate_cypher method."""
    
    def test_valid_simple_query(self, groq_translator):
        """Test validation of simple valid Cypher query."""
        cypher = "MATCH (o:Order) RETURN o.order_id"
        assert groq_translator._validate_cypher(cypher) is True
    
    def test_valid_complex_query(self, groq_translator):
        """Test validation of complex valid Cypher query."""
        cypher = """
        MATCH (o:Order)-[:DELIVERED_BY]->(d:Delivery)
        WHERE NOT EXISTS((o)-[:BILLED_BY]->(:Invoice))
        RETURN o.order_id, d.delivery_date
        """
        assert groq_translator._validate_cypher(cypher) is True
    
    def test_empty_query(self, groq_translator):
        """Test validation fails for empty query."""
        assert groq_translator._validate_cypher("") is False
        assert groq_translator._validate_cypher("   ") is False
    
    def test_missing_match_and_return(self, groq_translator):
        """Test validation fails without MATCH or RETURN."""
        cypher = "CREATE (n:Node)"
        # This should fail because it has neither MATCH nor RETURN
        # Actually CREATE is valid, let's test something truly invalid
        cypher = "SELECT * FROM orders"
        assert groq_translator._validate_cypher(cypher) is False
    
    def test_unbalanced_parentheses(self, groq_translator):
        """Test validation fails for unbalanced parentheses."""
        cypher = "MATCH (o:Order RETURN o"
        assert groq_translator._validate_cypher(cypher) is False
    
    def test_unbalanced_brackets(self, groq_translator):
        """Test validation fails for unbalanced brackets."""
        cypher = "MATCH (o:Order)-[:REL->(d:Delivery) RETURN o"
        assert groq_translator._validate_cypher(cypher) is False
    
    def test_unbalanced_braces(self, groq_translator):
        """Test validation fails for unbalanced braces."""
        cypher = "MATCH (o:Order {order_id: '123') RETURN o"
        assert groq_translator._validate_cypher(cypher) is False
    
    def test_unknown_node_label(self, groq_translator):
        """Test validation fails for unknown node labels."""
        cypher = "MATCH (x:UnknownLabel) RETURN x"
        assert groq_translator._validate_cypher(cypher) is False
    
    def test_valid_node_labels(self, groq_translator):
        """Test validation passes for known node labels."""
        cypher = "MATCH (o:Order)-[:CONTAINS]->(p:Product) RETURN o, p"
        assert groq_translator._validate_cypher(cypher) is True


class TestCleanCypherResponse:
    """Tests for _clean_cypher_response method."""
    
    def test_clean_markdown_code_block(self, groq_translator):
        """Test removal of markdown code blocks."""
        response = "```cypher\nMATCH (o:Order) RETURN o\n```"
        cleaned = groq_translator._clean_cypher_response(response)
        assert cleaned == "MATCH (o:Order) RETURN o"
    
    def test_clean_prefix(self, groq_translator):
        """Test removal of common prefixes."""
        response = "Cypher query: MATCH (o:Order) RETURN o"
        cleaned = groq_translator._clean_cypher_response(response)
        assert cleaned == "MATCH (o:Order) RETURN o"
    
    def test_clean_multiline_with_explanation(self, groq_translator):
        """Test extraction of query from multiline response."""
        response = """Here's the query:
MATCH (o:Order) RETURN o
This query returns all orders."""
        cleaned = groq_translator._clean_cypher_response(response)
        assert "MATCH (o:Order) RETURN o" in cleaned
    
    def test_clean_already_clean(self, groq_translator):
        """Test that clean query remains unchanged."""
        response = "MATCH (o:Order) RETURN o"
        cleaned = groq_translator._clean_cypher_response(response)
        assert cleaned == response


class TestTranslateMethod:
    """Tests for translate method."""
    
    def test_translate_empty_query(self, groq_translator):
        """Test translation of empty query returns error."""
        result = groq_translator.translate("")
        assert result.success is False
        assert "empty" in result.error.lower()
    
    @patch('backend.app.services.query_translator.httpx.Client')
    def test_translate_success_groq(self, mock_client, groq_translator):
        """Test successful translation with Groq."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "MATCH (o:Order) RETURN o LIMIT 20"
                    }
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = groq_translator.translate("Show me all orders")
        
        assert result.success is True
        assert "MATCH" in result.cypher
        assert result.error is None
    
    @patch('backend.app.services.query_translator.httpx.Client')
    def test_translate_success_gemini(self, mock_client, gemini_translator):
        """Test successful translation with Gemini."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "MATCH (o:Order) RETURN o LIMIT 20"
                            }
                        ]
                    }
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = gemini_translator.translate("Show me all orders")
        
        assert result.success is True
        assert "MATCH" in result.cypher
        assert result.error is None
    
    @patch('backend.app.services.query_translator.httpx.Client')
    def test_translate_retry_on_invalid_cypher(self, mock_client, groq_translator):
        """Test retry logic when invalid Cypher is generated."""
        # First call returns invalid Cypher, second call returns valid
        mock_response1 = Mock()
        mock_response1.json.return_value = {
            "choices": [{"message": {"content": "INVALID QUERY"}}]
        }
        mock_response1.raise_for_status = Mock()
        
        mock_response2 = Mock()
        mock_response2.json.return_value = {
            "choices": [{"message": {"content": "MATCH (o:Order) RETURN o"}}]
        }
        mock_response2.raise_for_status = Mock()
        
        mock_client_instance = Mock()
        mock_client_instance.post.side_effect = [mock_response1, mock_response2]
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = groq_translator.translate("Show me orders")
        
        assert result.success is True
        assert mock_client_instance.post.call_count == 2
    
    @patch('backend.app.services.query_translator.httpx.Client')
    def test_translate_max_retries_exceeded(self, mock_client, groq_translator):
        """Test failure after max retries exceeded."""
        # All calls return invalid Cypher
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "INVALID"}}]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = groq_translator.translate("Show me orders", max_retries=2)
        
        assert result.success is False
        assert "validation" in result.error.lower()
        assert mock_client_instance.post.call_count == 3  # Initial + 2 retries
    
    @patch('backend.app.services.query_translator.httpx.Client')
    def test_translate_api_error(self, mock_client, groq_translator):
        """Test handling of API errors."""
        mock_client_instance = Mock()
        mock_client_instance.post.side_effect = Exception("API Error")
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = groq_translator.translate("Show me orders", max_retries=1)
        
        assert result.success is False
        assert "API Error" in result.error


class TestGroqAPICall:
    """Tests for _call_groq method."""
    
    @patch('backend.app.services.query_translator.httpx.Client')
    def test_call_groq_success(self, mock_client, groq_translator):
        """Test successful Groq API call."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "MATCH (o:Order) RETURN o"
                    }
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = groq_translator._call_groq("test prompt")
        
        assert result == "MATCH (o:Order) RETURN o"
        assert mock_client_instance.post.called
    
    @patch('backend.app.services.query_translator.httpx.Client')
    def test_call_groq_with_markdown(self, mock_client, groq_translator):
        """Test Groq API call with markdown in response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "```cypher\nMATCH (o:Order) RETURN o\n```"
                    }
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = groq_translator._call_groq("test prompt")
        
        assert result == "MATCH (o:Order) RETURN o"


class TestGeminiAPICall:
    """Tests for _call_gemini method."""
    
    @patch('backend.app.services.query_translator.httpx.Client')
    def test_call_gemini_success(self, mock_client, gemini_translator):
        """Test successful Gemini API call."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "MATCH (o:Order) RETURN o"
                            }
                        ]
                    }
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = gemini_translator._call_gemini("test prompt")
        
        assert result == "MATCH (o:Order) RETURN o"
        assert mock_client_instance.post.called
    
    @patch('backend.app.services.query_translator.httpx.Client')
    def test_call_gemini_with_markdown(self, mock_client, gemini_translator):
        """Test Gemini API call with markdown in response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "```cypher\nMATCH (o:Order) RETURN o\n```"
                            }
                        ]
                    }
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = gemini_translator._call_gemini("test prompt")
        
        assert result == "MATCH (o:Order) RETURN o"
