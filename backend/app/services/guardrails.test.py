"""
Unit tests for GuardrailSystem

Tests cover query classification for in-domain business queries,
out-of-domain query rejection, edge cases, and logging behavior.
"""

import pytest
from unittest.mock import patch
from app.services.guardrails import GuardrailSystem, QueryClassification


class TestGuardrailSystemInitialization:
    """Test GuardrailSystem initialization."""
    
    def test_successful_initialization(self):
        """Test successful initialization of GuardrailSystem."""
        system = GuardrailSystem()
        assert system is not None
        assert len(system.IN_DOMAIN_KEYWORDS) > 0
        assert len(system.OUT_OF_DOMAIN_KEYWORDS) > 0


class TestInDomainQueries:
    """Test classification of valid in-domain business queries."""
    
    @pytest.fixture
    def guardrail(self):
        """Create a GuardrailSystem instance."""
        return GuardrailSystem()
    
    def test_order_query(self, guardrail):
        """Test query about orders is accepted."""
        result = guardrail.classify_query("Show me all orders from last month")
        assert result.is_valid is True
        assert result.reason is None
    
    def test_delivery_query(self, guardrail):
        """Test query about deliveries is accepted."""
        result = guardrail.classify_query("Which deliveries are in transit?")
        assert result.is_valid is True
        assert result.reason is None
    
    def test_invoice_query(self, guardrail):
        """Test query about invoices is accepted."""
        result = guardrail.classify_query("Find all unpaid invoices")
        assert result.is_valid is True
        assert result.reason is None
    
    def test_payment_query(self, guardrail):
        """Test query about payments is accepted."""
        result = guardrail.classify_query("Show me payments made this week")
        assert result.is_valid is True
        assert result.reason is None
    
    def test_customer_query(self, guardrail):
        """Test query about customers is accepted."""
        result = guardrail.classify_query("List all customers in New York")
        assert result.is_valid is True
        assert result.reason is None
    
    def test_product_query(self, guardrail):
        """Test query about products is accepted."""
        result = guardrail.classify_query("What are the top selling products?")
        assert result.is_valid is True
        assert result.reason is None
    
    def test_address_query(self, guardrail):
        """Test query about addresses is accepted."""
        result = guardrail.classify_query("Show me all shipping addresses in California")
        assert result.is_valid is True
        assert result.reason is None
    
    def test_flow_tracing_query(self, guardrail):
        """Test query about flow tracing is accepted."""
        result = guardrail.classify_query("Trace the complete flow for order 12345")
        assert result.is_valid is True
        assert result.reason is None
    
    def test_broken_flow_query(self, guardrail):
        """Test query about broken flows is accepted."""
        result = guardrail.classify_query("Find orders that have been delivered but not billed")
        assert result.is_valid is True
        assert result.reason is None
    
    def test_billing_query(self, guardrail):
        """Test query about billing is accepted."""
        result = guardrail.classify_query("Which products have the most billing documents?")
        assert result.is_valid is True
        assert result.reason is None
    
    def test_shipping_query(self, guardrail):
        """Test query about shipping is accepted."""
        result = guardrail.classify_query("Show me all orders that haven't been shipped yet")
        assert result.is_valid is True
        assert result.reason is None
    
    def test_aggregation_query(self, guardrail):
        """Test aggregation query is accepted."""
        result = guardrail.classify_query("How many orders were placed last quarter?")
        assert result.is_valid is True
        assert result.reason is None
    
    def test_status_query(self, guardrail):
        """Test query about status is accepted."""
        result = guardrail.classify_query("What is the status of delivery DEL-123?")
        assert result.is_valid is True
        assert result.reason is None
    
    def test_case_insensitive_matching(self, guardrail):
        """Test that keyword matching is case-insensitive."""
        result = guardrail.classify_query("SHOW ME ALL ORDERS")
        assert result.is_valid is True
        
        result = guardrail.classify_query("Show Me All Orders")
        assert result.is_valid is True
        
        result = guardrail.classify_query("show me all orders")
        assert result.is_valid is True
    
    def test_multiple_keywords(self, guardrail):
        """Test query with multiple in-domain keywords."""
        result = guardrail.classify_query(
            "Show me customers who have orders without payments"
        )
        assert result.is_valid is True


class TestOutOfDomainQueries:
    """Test rejection of out-of-domain queries."""
    
    @pytest.fixture
    def guardrail(self):
        """Create a GuardrailSystem instance."""
        return GuardrailSystem()
    
    def test_weather_query(self, guardrail):
        """Test weather query is rejected."""
        result = guardrail.classify_query("What's the weather like today?")
        assert result.is_valid is False
        assert result.reason is not None
        assert "outside the business intelligence domain" in result.reason
    
    def test_sports_query(self, guardrail):
        """Test sports query is rejected."""
        result = guardrail.classify_query("Who won the game last night?")
        assert result.is_valid is False
        assert result.reason is not None
    
    def test_news_query(self, guardrail):
        """Test news query is rejected."""
        result = guardrail.classify_query("What's the latest news today?")
        assert result.is_valid is False
        assert result.reason is not None
    
    def test_personal_advice_query(self, guardrail):
        """Test personal advice query is rejected."""
        result = guardrail.classify_query("What should I do about my problem?")
        assert result.is_valid is False
        assert result.reason is not None
    
    def test_general_knowledge_query(self, guardrail):
        """Test general knowledge query is rejected."""
        result = guardrail.classify_query("Who is the president of France?")
        assert result.is_valid is False
        assert result.reason is not None
    
    def test_movie_query(self, guardrail):
        """Test movie query is rejected."""
        result = guardrail.classify_query("What's the best movie of 2024?")
        assert result.is_valid is False
        assert result.reason is not None
    
    def test_music_query(self, guardrail):
        """Test music query is rejected."""
        result = guardrail.classify_query("What's the latest song by Taylor Swift?")
        assert result.is_valid is False
        assert result.reason is not None
    
    def test_recipe_query(self, guardrail):
        """Test recipe query is rejected."""
        result = guardrail.classify_query("How do I cook pasta?")
        assert result.is_valid is False
        assert result.reason is not None
    
    def test_travel_query(self, guardrail):
        """Test travel query is rejected."""
        result = guardrail.classify_query("What's the best vacation destination?")
        assert result.is_valid is False
        assert result.reason is not None
    
    def test_health_query(self, guardrail):
        """Test health query is rejected."""
        result = guardrail.classify_query("What are the symptoms of flu?")
        assert result.is_valid is False
        assert result.reason is not None
    
    def test_politics_query(self, guardrail):
        """Test politics query is rejected."""
        result = guardrail.classify_query("Who won the election?")
        assert result.is_valid is False
        assert result.reason is not None
    
    def test_celebrity_query(self, guardrail):
        """Test celebrity query is rejected."""
        result = guardrail.classify_query("Tell me about a famous actor")
        assert result.is_valid is False
        assert result.reason is not None


class TestEdgeCases:
    """Test edge cases and ambiguous queries."""
    
    @pytest.fixture
    def guardrail(self):
        """Create a GuardrailSystem instance."""
        return GuardrailSystem()
    
    def test_empty_query(self, guardrail):
        """Test empty query is rejected."""
        result = guardrail.classify_query("")
        assert result.is_valid is False
        assert result.reason == "Query cannot be empty"
    
    def test_whitespace_only_query(self, guardrail):
        """Test whitespace-only query is rejected."""
        result = guardrail.classify_query("   ")
        assert result.is_valid is False
        assert result.reason == "Query cannot be empty"
    
    def test_none_query(self, guardrail):
        """Test None query is rejected."""
        result = guardrail.classify_query(None)
        assert result.is_valid is False
        assert result.reason == "Query cannot be empty"
    
    def test_ambiguous_query_no_keywords(self, guardrail):
        """Test query with no clear domain keywords is rejected."""
        result = guardrail.classify_query("Tell me something interesting")
        assert result.is_valid is False
        assert "Unable to determine" in result.reason
    
    def test_query_with_both_domain_types(self, guardrail):
        """Test query with both in-domain and out-of-domain keywords."""
        # Out-of-domain keywords take precedence
        result = guardrail.classify_query(
            "What's the weather like for order deliveries?"
        )
        assert result.is_valid is False
        assert "outside the business intelligence domain" in result.reason
    
    def test_very_short_query(self, guardrail):
        """Test very short query with valid keyword."""
        result = guardrail.classify_query("orders")
        assert result.is_valid is True
    
    def test_very_long_query(self, guardrail):
        """Test very long query with valid keywords."""
        long_query = (
            "I would like to see a comprehensive analysis of all orders "
            "that were placed in the last quarter, including their delivery "
            "status, invoice amounts, and payment information, grouped by "
            "customer and product category"
        )
        result = guardrail.classify_query(long_query)
        assert result.is_valid is True
    
    def test_query_with_special_characters(self, guardrail):
        """Test query with special characters."""
        result = guardrail.classify_query("Show me order #12345!")
        assert result.is_valid is True
    
    def test_query_with_numbers(self, guardrail):
        """Test query with numbers."""
        result = guardrail.classify_query("Find orders with amount > 1000")
        assert result.is_valid is True


class TestLogging:
    """Test logging behavior for query classification."""
    
    @pytest.fixture
    def guardrail(self):
        """Create a GuardrailSystem instance."""
        return GuardrailSystem()
    
    def test_logging_accepted_query(self, guardrail):
        """Test that accepted queries are logged."""
        with patch('app.services.guardrails.logger') as mock_logger:
            guardrail.classify_query("Show me all orders")
            
            # Check that info was logged for accepted query
            assert mock_logger.info.called
            info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("accepted" in call.lower() for call in info_calls)
    
    def test_logging_rejected_query(self, guardrail):
        """Test that rejected queries are logged."""
        with patch('app.services.guardrails.logger') as mock_logger:
            guardrail.classify_query("What's the weather?")
            
            # Check that info was logged for rejected query
            assert mock_logger.info.called
            info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("rejected" in call.lower() for call in info_calls)
    
    def test_logging_empty_query(self, guardrail):
        """Test that empty queries are logged as warnings."""
        with patch('app.services.guardrails.logger') as mock_logger:
            guardrail.classify_query("")
            
            # Check that warning was logged
            mock_logger.warning.assert_called_once()
    
    def test_logging_includes_query_text(self, guardrail):
        """Test that rejected query text is logged."""
        with patch('app.services.guardrails.logger') as mock_logger:
            test_query = "What's the weather forecast?"
            guardrail.classify_query(test_query)
            
            # Check that the query text appears in logs
            info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any(test_query in call for call in info_calls)


class TestQueryClassificationModel:
    """Test QueryClassification Pydantic model."""
    
    def test_valid_classification(self):
        """Test creating valid QueryClassification."""
        classification = QueryClassification(is_valid=True)
        assert classification.is_valid is True
        assert classification.reason is None
    
    def test_invalid_classification_with_reason(self):
        """Test creating invalid QueryClassification with reason."""
        classification = QueryClassification(
            is_valid=False,
            reason="Query is out of domain"
        )
        assert classification.is_valid is False
        assert classification.reason == "Query is out of domain"
    
    def test_classification_serialization(self):
        """Test QueryClassification can be serialized to dict."""
        classification = QueryClassification(
            is_valid=False,
            reason="Test reason"
        )
        data = classification.model_dump()
        assert data["is_valid"] is False
        assert data["reason"] == "Test reason"
