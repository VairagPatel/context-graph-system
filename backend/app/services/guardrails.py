"""
Guardrail System for Query Validation

This module implements domain-specific query validation to ensure queries
are restricted to the business intelligence domain. It classifies queries
as in-domain or out-of-domain based on keyword analysis.
"""

import logging
from typing import Optional
from pydantic import BaseModel


# Configure logging
logger = logging.getLogger(__name__)


class QueryClassification(BaseModel):
    """Result of query classification."""
    is_valid: bool
    reason: Optional[str] = None


class GuardrailSystem:
    """
    Validates that queries are within the business intelligence domain.
    
    Uses keyword-based classification to identify queries about business
    entities (Orders, Deliveries, Invoices, Payments, Customers, Products,
    Addresses) and reject queries about unrelated topics.
    """
    
    # Keywords indicating in-domain business intelligence queries
    IN_DOMAIN_KEYWORDS = {
        # General business terms
        "order", "orders",
        "delivery", "deliveries", "delivered", "shipping", "shipped", "ship",
        "invoice", "invoices", "billing", "billed", "bill",
        "payment", "payments", "paid", "pay",
        "customer", "customers", "client", "clients",
        "product", "products", "item", "items",
        "address", "addresses", "location", "locations",
        "flow", "flows", "trace", "traced", "tracing",
        "process", "processes",
        "sales", "purchase", "purchases", "bought",
        "amount", "total", "price", "cost",
        "status", "tracking",
        "date", "time", "when",
        "count", "number", "how many", "top", "most", "least",
        "broken", "incomplete", "missing", "without",
        
        # SAP O2C specific terms
        "sales order", "salesorder", "so",
        "outbound delivery", "delivery document",
        "billing document", "billingdocument",
        "journal entry", "accounting document",
        "business partner", "businesspartner", "bp",
        "material", "materials",
        "plant", "plants", "warehouse",
        "goods movement", "picking",
        "accounts receivable", "ar",
        "clearing", "cleared",
        "fiscal year", "company code",
        "sold to party", "ship to party",
        "net amount", "gross amount",
        "transaction currency",
        "o2c", "order to cash", "order-to-cash",
        "procure to pay", "p2p",
        "quote to cash", "q2c",
    }
    
    # Keywords indicating out-of-domain queries
    OUT_OF_DOMAIN_KEYWORDS = {
        "weather", "forecast", "temperature", "rain", "snow", "climate",
        "sports", "game", "score", "team", "player", "match", "tournament",
        "news", "article", "headline", "breaking", "latest news",
        "personal", "advice", "help me", "what should i", "recommend",
        "general knowledge", "who is", "what is", "define", "explain",
        "movie", "film", "actor", "actress", "director",
        "music", "song", "artist", "album", "concert",
        "recipe", "cooking", "food", "restaurant",
        "travel", "vacation", "hotel", "flight", "destination",
        "health", "medical", "doctor", "symptom", "disease",
        "politics", "election", "government", "president", "vote",
        "celebrity", "famous", "star",
    }
    
    def __init__(self):
        """Initialize the GuardrailSystem."""
        logger.info("GuardrailSystem initialized")
    
    def classify_query(self, query: str) -> QueryClassification:
        """
        Classifies query as in-domain or out-of-domain.
        
        Args:
            query: Natural language query string
            
        Returns:
            QueryClassification with is_valid=True if in-domain,
            is_valid=False with reason if out-of-domain
        """
        if not query or not query.strip():
            logger.warning("Empty query received")
            return QueryClassification(
                is_valid=False,
                reason="Query cannot be empty"
            )
        
        # Normalize query for keyword matching
        query_lower = query.lower()
        
        # Check for out-of-domain keywords first (more specific)
        out_domain_matches = [
            keyword for keyword in self.OUT_OF_DOMAIN_KEYWORDS
            if keyword in query_lower
        ]
        
        if out_domain_matches:
            reason = (
                f"Query appears to be about topics outside the business intelligence domain. "
                f"This system only answers questions about orders, deliveries, invoices, "
                f"payments, customers, products, and addresses."
            )
            logger.info(f"Query rejected - out-of-domain keywords found: {out_domain_matches}")
            logger.info(f"Rejected query: {query}")
            return QueryClassification(
                is_valid=False,
                reason=reason
            )
        
        # Check for in-domain keywords
        in_domain_matches = [
            keyword for keyword in self.IN_DOMAIN_KEYWORDS
            if keyword in query_lower
        ]
        
        if in_domain_matches:
            logger.info(f"Query accepted - in-domain keywords found: {in_domain_matches}")
            return QueryClassification(is_valid=True)
        
        # If no clear domain indicators, reject with helpful message
        reason = (
            "Unable to determine if query is related to business data. "
            "Please ask questions about orders, deliveries, invoices, payments, "
            "customers, products, or addresses."
        )
        logger.info(f"Query rejected - no domain keywords found")
        logger.info(f"Rejected query: {query}")
        return QueryClassification(
            is_valid=False,
            reason=reason
        )
