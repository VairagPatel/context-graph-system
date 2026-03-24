"""
Query Translator Service

This module implements LLM-powered translation of natural language queries
to Cypher queries. It supports both Groq and Gemini API providers and includes
prompt engineering with schema context and few-shot examples.
"""

import logging
import re
from typing import Optional, Dict, Any
from pydantic import BaseModel
import httpx


logger = logging.getLogger(__name__)


class TranslationResult(BaseModel):
    """Result of query translation."""
    cypher: str
    success: bool
    error: Optional[str] = None


class GraphSchema(BaseModel):
    """Graph schema definition for prompt context."""
    node_types: Dict[str, list]  # label -> list of properties
    relationship_types: list  # list of relationship type names


class QueryTranslator:
    """
    Converts natural language queries to Cypher using LLM providers.
    
    Supports Groq and Gemini APIs with retry logic and basic Cypher validation.
    Uses few-shot prompting with schema context for accurate translations.
    """
    
    # API endpoints
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    # Default model names
    GROQ_MODEL = "llama-3.3-70b-versatile"
    
    def __init__(self, llm_provider: str, api_key: str, schema: GraphSchema):
        """
        Initialize QueryTranslator with LLM provider and schema.
        
        Args:
            llm_provider: Either "groq" or "gemini"
            api_key: API key for the LLM provider
            schema: GraphSchema containing node types and relationship types
        
        Raises:
            ValueError: If llm_provider is not "groq" or "gemini"
        """
        if llm_provider.lower() not in ["groq", "gemini"]:
            raise ValueError("llm_provider must be 'groq' or 'gemini'")
        
        self.llm_provider = llm_provider.lower()
        self.api_key = api_key
        self.schema = schema
        
        logger.info(f"QueryTranslator initialized with provider: {self.llm_provider}")
    
    def translate(self, natural_language_query: str, max_retries: int = 2) -> TranslationResult:
        """
        Translate natural language query to Cypher.
        
        Args:
            natural_language_query: User's question in natural language
            max_retries: Maximum number of retry attempts (default: 2)
        
        Returns:
            TranslationResult with cypher query or error
        """
        if not natural_language_query or not natural_language_query.strip():
            return TranslationResult(
                cypher="",
                success=False,
                error="Query cannot be empty"
            )
        
        # Build prompt with schema and examples
        prompt = self._build_prompt(natural_language_query)
        
        # Attempt translation with retries
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Translation attempt {attempt + 1}/{max_retries + 1}")
                
                # Call LLM provider
                if self.llm_provider == "groq":
                    cypher = self._call_groq(prompt)
                else:  # gemini
                    cypher = self._call_gemini(prompt)
                
                # Validate Cypher syntax
                if self._validate_cypher(cypher):
                    logger.info("Translation successful")
                    return TranslationResult(
                        cypher=cypher,
                        success=True
                    )
                else:
                    logger.warning(f"Invalid Cypher generated: {cypher}")
                    if attempt == max_retries:
                        return TranslationResult(
                            cypher="",
                            success=False,
                            error="Generated Cypher failed validation"
                        )
            
            except Exception as e:
                logger.error(f"Translation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries:
                    return TranslationResult(
                        cypher="",
                        success=False,
                        error=f"Translation failed after {max_retries + 1} attempts: {str(e)}"
                    )
        
        return TranslationResult(
            cypher="",
            success=False,
            error="Translation failed"
        )
    
    def _build_prompt(self, query: str) -> str:
        """
        Build LLM prompt with schema context and few-shot examples.
        
        Args:
            query: Natural language query
        
        Returns:
            Complete prompt string
        """
        # Build schema description
        schema_desc = "SCHEMA:\n"
        schema_desc += "Nodes:\n"
        for label, properties in self.schema.node_types.items():
            props_str = ", ".join(properties)
            schema_desc += f"  {label}({props_str})\n"
        
        schema_desc += "\nRelationships:\n"
        for rel_type in self.schema.relationship_types:
            schema_desc += f"  {rel_type}\n"
        
        # Few-shot examples covering common patterns
        examples = """
EXAMPLES:

Q: "Show me the top 10 products by number of sales orders"
A: MATCH (p:Product)<-[:CONTAINS_PRODUCT]-(soi:SalesOrderItem)-[:BELONGS_TO_ORDER]->(so:SalesOrder) RETURN p.product, p.productType, COUNT(DISTINCT so) AS order_count ORDER BY order_count DESC LIMIT 10

Q: "Trace the complete O2C flow for sales order 740506"
A: MATCH (so:SalesOrder {salesOrder: '740506'}) OPTIONAL MATCH (so)<-[:BELONGS_TO_ORDER]-(soi:SalesOrderItem) OPTIONAL MATCH (soi)-[:CONTAINS_PRODUCT]->(p:Product) OPTIONAL MATCH (so)<-[:FULFILLS_ORDER]-(di:DeliveryItem)-[:BELONGS_TO_DELIVERY]->(d:Delivery) OPTIONAL MATCH (so)<-[:BILLS_ORDER]-(bi:BillingDocumentItem)-[:BELONGS_TO_BILLING]->(bd:BillingDocument) OPTIONAL MATCH (bd)-[:CREATES_JOURNAL_ENTRY]->(je:JournalEntry) OPTIONAL MATCH (je)<-[:CLEARS_JOURNAL_ENTRY]-(pay:Payment) RETURN so, soi, p, d, di, bd, bi, je, pay

Q: "Which business partners have the most sales orders?"
A: MATCH (bp:BusinessPartner)<-[:SOLD_TO_CUSTOMER]-(so:SalesOrder) RETURN bp.businessPartner, bp.businessPartnerFullName, COUNT(so) AS order_count ORDER BY order_count DESC LIMIT 10

Q: "Find sales orders that have been delivered but not billed"
A: MATCH (so:SalesOrder)<-[:FULFILLS_ORDER]-(di:DeliveryItem)-[:BELONGS_TO_DELIVERY]->(d:Delivery) WHERE NOT EXISTS((so)<-[:BILLS_ORDER]-(:BillingDocumentItem)) RETURN so.salesOrder, so.creationDate, so.totalNetAmount, d.deliveryDocument, d.creationDate AS delivery_date ORDER BY so.creationDate DESC LIMIT 20

Q: "Show me billing documents without payments"
A: MATCH (bd:BillingDocument) WHERE NOT EXISTS((bd)-[:CREATES_JOURNAL_ENTRY]->(:JournalEntry)<-[:CLEARS_JOURNAL_ENTRY]-(:Payment)) RETURN bd.billingDocument, bd.billingDocumentDate, bd.totalNetAmount, bd.soldToParty ORDER BY bd.billingDocumentDate DESC LIMIT 20

Q: "Which products are shipped from plant 1920?"
A: MATCH (p:Product)<-[:CONTAINS_PRODUCT]-(soi:SalesOrderItem)-[:SHIPS_FROM_PLANT]->(pl:Plant {plant: '1920'}) RETURN DISTINCT p.product, p.productType, p.productGroup, COUNT(soi) AS shipment_count ORDER BY shipment_count DESC LIMIT 20

Q: "Find blocked business partners"
A: MATCH (bp:BusinessPartner) WHERE bp.businessPartnerIsBlocked = true RETURN bp.businessPartner, bp.businessPartnerFullName, bp.businessPartnerCategory LIMIT 20

Q: "What is the total net amount of all billing documents?"
A: MATCH (bd:BillingDocument) RETURN SUM(toFloat(bd.totalNetAmount)) AS total_revenue, COUNT(bd) AS billing_document_count

Q: "Show me recent deliveries"
A: MATCH (d:Delivery) RETURN d.deliveryDocument, d.creationDate, d.shippingPoint, d.overallGoodsMovementStatus ORDER BY d.creationDate DESC LIMIT 20

Q: "Find all sales orders for customer 320000083"
A: MATCH (bp:BusinessPartner {businessPartner: '320000083'})<-[:SOLD_TO_CUSTOMER]-(so:SalesOrder) RETURN so.salesOrder, so.creationDate, so.totalNetAmount, so.transactionCurrency ORDER BY so.creationDate DESC LIMIT 20

Q: "Which materials are most frequently ordered?"
A: MATCH (p:Product)<-[:CONTAINS_PRODUCT]-(soi:SalesOrderItem) RETURN p.product, p.productType, COUNT(soi) AS order_frequency ORDER BY order_frequency DESC LIMIT 10

Q: "Show me payments cleared in April 2025"
A: MATCH (pay:Payment) WHERE pay.clearingDate >= '2025-04-01' AND pay.clearingDate < '2025-05-01' RETURN pay.accountingDocument, pay.clearingDate, pay.amountInTransactionCurrency, pay.customer ORDER BY pay.clearingDate DESC LIMIT 20

Q: "Find incomplete O2C flows"
A: MATCH (so:SalesOrder) WHERE NOT EXISTS((so)<-[:FULFILLS_ORDER]-(:DeliveryItem)) OR NOT EXISTS((so)<-[:BILLS_ORDER]-(:BillingDocumentItem)) RETURN so.salesOrder, so.creationDate, so.totalNetAmount, CASE WHEN NOT EXISTS((so)<-[:FULFILLS_ORDER]-(:DeliveryItem)) THEN 'Missing Delivery' WHEN NOT EXISTS((so)<-[:BILLS_ORDER]-(:BillingDocumentItem)) THEN 'Missing Billing' ELSE 'Unknown' END AS issue ORDER BY so.creationDate DESC LIMIT 20

Q: "List all products with their descriptions"
A: MATCH (p:Product) OPTIONAL MATCH (p)<-[:DESCRIBES_PRODUCT]-(pd:ProductDescription) RETURN p.product, p.productType, p.productGroup, pd.productDescription LIMIT 20
"""
        
        # Instructions
        instructions = """
INSTRUCTIONS:
- Return ONLY the Cypher query without any explanation or markdown formatting
- Use LIMIT 20 by default unless the user specifies a different limit
- Use OPTIONAL MATCH for relationships that might not exist
- Always include relevant properties in the RETURN clause
- Use ORDER BY for ranked results
- Use COUNT, SUM, AVG for aggregations
- Use WHERE clauses for filtering
- Ensure all node labels and relationship types match the schema exactly
"""
        
        # Combine all parts
        prompt = f"""You are a Cypher query generator for a business intelligence graph database.

{schema_desc}
{examples}
{instructions}

USER QUERY: {query}

Cypher query:"""
        
        return prompt
    
    def _validate_cypher(self, cypher: str) -> bool:
        """
        Perform basic syntax validation on generated Cypher.
        
        Args:
            cypher: Cypher query string
        
        Returns:
            True if validation passes, False otherwise
        """
        if not cypher or not cypher.strip():
            return False
        
        cypher_upper = cypher.upper()
        
        # Check for basic Cypher keywords
        has_match = "MATCH" in cypher_upper
        has_return = "RETURN" in cypher_upper
        
        if not (has_match or has_return):
            logger.warning("Cypher missing MATCH or RETURN clause")
            return False
        
        # Check for balanced parentheses
        if cypher.count("(") != cypher.count(")"):
            logger.warning("Unbalanced parentheses in Cypher")
            return False
        
        # Check for balanced brackets
        if cypher.count("[") != cypher.count("]"):
            logger.warning("Unbalanced brackets in Cypher")
            return False
        
        # Check for balanced braces
        if cypher.count("{") != cypher.count("}"):
            logger.warning("Unbalanced braces in Cypher")
            return False
        
        # Check that node labels exist in schema
        node_pattern = r'\((\w+):(\w+)'
        matches = re.findall(node_pattern, cypher)
        for _, label in matches:
            if label not in self.schema.node_types:
                logger.warning(f"Unknown node label in Cypher: {label}")
                return False
        
        return True
    
    def _call_groq(self, prompt: str) -> str:
        """
        Call Groq API to generate Cypher query.
        
        Args:
            prompt: Complete prompt with schema and examples
        
        Returns:
            Generated Cypher query
        
        Raises:
            Exception: If API call fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.GROQ_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,  # Low temperature for consistent output
            "max_tokens": 500
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                self.GROQ_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            cypher = data["choices"][0]["message"]["content"].strip()
            
            # Clean up response (remove markdown code blocks if present)
            cypher = self._clean_cypher_response(cypher)
            
            return cypher
    
    def _call_gemini(self, prompt: str) -> str:
        """
        Call Gemini API to generate Cypher query.
        
        Args:
            prompt: Complete prompt with schema and examples
        
        Returns:
            Generated Cypher query
        
        Raises:
            Exception: If API call fails
        """
        url = f"{self.GEMINI_API_URL}?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 500
            }
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            cypher = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            # Clean up response (remove markdown code blocks if present)
            cypher = self._clean_cypher_response(cypher)
            
            return cypher
    
    def _clean_cypher_response(self, response: str) -> str:
        """
        Clean LLM response to extract pure Cypher query.
        
        Args:
            response: Raw LLM response
        
        Returns:
            Cleaned Cypher query
        """
        # Remove markdown code blocks
        response = re.sub(r'```cypher\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        # Remove common prefixes
        response = re.sub(r'^(Cypher query:|Query:|A:)\s*', '', response, flags=re.IGNORECASE)
        
        # Take only the first line if multiple lines with explanations
        lines = response.strip().split('\n')
        if len(lines) > 1:
            # Find the line that looks most like a Cypher query
            for line in lines:
                line_upper = line.strip().upper()
                if any(keyword in line_upper for keyword in ['MATCH', 'CREATE', 'MERGE', 'RETURN']):
                    return line.strip()
        
        return response.strip()
