# Requirements Document

## Introduction

This document specifies requirements for a Graph-Based Data Modeling and Query System designed for business intelligence applications. The system converts fragmented relational business data into a unified graph representation, provides interactive visualization, and enables natural language querying through LLM-powered query translation. The system focuses on business process flows including Orders, Deliveries, Invoices, and Payments.

## Glossary

- **Graph_Database**: Neo4j database storing business entities as nodes and relationships as edges
- **API_Server**: FastAPI backend service handling HTTP requests and database operations
- **Web_Client**: React-based frontend application providing user interface
- **Graph_Visualizer**: React Flow component rendering interactive graph visualization
- **Query_Translator**: LLM-powered service converting natural language to Cypher queries
- **Chat_Interface**: Conversational UI component for natural language queries
- **Guardrail_System**: Validation layer restricting queries to dataset domain
- **Business_Entity**: Core data objects (Orders, Deliveries, Invoices, Payments, Customers, Products, Addresses)
- **Cypher_Query**: Neo4j graph database query language statement
- **Natural_Language_Query**: User-provided question in conversational English
- **Query_Response**: Structured data result from executed database query
- **LLM_Provider**: External language model service (Groq or Gemini free tier)
- **Graph_Schema**: Defined structure of nodes, relationships, and properties in the graph
- **Flow_Trace**: Complete path through related business entities (e.g., Order → Delivery → Invoice → Payment)

## Requirements

### Requirement 1: Data Import and Graph Construction

**User Story:** As a business analyst, I want to import relational business data into a graph database, so that I can analyze relationships and flows between entities.

#### Acceptance Criteria

1. THE API_Server SHALL accept CSV or JSON files containing business entity data
2. WHEN valid business data is uploaded, THE API_Server SHALL parse the data and validate required fields
3. WHEN data validation succeeds, THE API_Server SHALL create nodes in the Graph_Database for each Business_Entity
4. THE API_Server SHALL establish edges between related Business_Entities based on foreign key relationships
5. WHEN graph construction completes, THE API_Server SHALL return a success status with entity and relationship counts
6. IF data validation fails, THEN THE API_Server SHALL return error messages identifying invalid records

### Requirement 2: Graph Schema Definition

**User Story:** As a system administrator, I want a well-defined graph schema, so that queries and visualizations are consistent and predictable.

#### Acceptance Criteria

1. THE Graph_Database SHALL store Orders as nodes with properties: order_id, customer_id, order_date, total_amount, status
2. THE Graph_Database SHALL store Deliveries as nodes with properties: delivery_id, order_id, delivery_date, status, tracking_number
3. THE Graph_Database SHALL store Invoices as nodes with properties: invoice_id, order_id, invoice_date, amount, status
4. THE Graph_Database SHALL store Payments as nodes with properties: payment_id, invoice_id, payment_date, amount, payment_method
5. THE Graph_Database SHALL store Customers as nodes with properties: customer_id, name, email, phone, address_id
6. THE Graph_Database SHALL store Products as nodes with properties: product_id, name, category, price, sku
7. THE Graph_Database SHALL store Addresses as nodes with properties: address_id, street, city, state, postal_code, country
8. THE Graph_Database SHALL define relationship types: CONTAINS, DELIVERED_BY, BILLED_BY, PAID_BY, PURCHASED_BY, SHIPS_TO, INCLUDES_PRODUCT

### Requirement 3: Interactive Graph Visualization

**User Story:** As a business analyst, I want to visualize the business data as an interactive graph, so that I can explore relationships visually.

#### Acceptance Criteria

1. THE Graph_Visualizer SHALL render nodes representing Business_Entities with distinct visual styles per entity type
2. THE Graph_Visualizer SHALL render edges representing relationships between Business_Entities
3. WHEN a user clicks on a node, THE Graph_Visualizer SHALL display the node's properties in a detail panel
4. WHEN a user clicks on an edge, THE Graph_Visualizer SHALL display the relationship type and properties
5. THE Graph_Visualizer SHALL support pan and zoom interactions for navigating large graphs
6. THE Graph_Visualizer SHALL support node dragging for manual layout adjustment
7. THE Web_Client SHALL fetch graph data from the API_Server and pass it to the Graph_Visualizer
8. WHEN the graph contains more than 100 nodes, THE Graph_Visualizer SHALL apply automatic layout algorithms for readability

### Requirement 4: Natural Language Query Interface

**User Story:** As a business analyst, I want to ask questions in natural language, so that I can query data without learning query languages.

#### Acceptance Criteria

1. THE Chat_Interface SHALL accept Natural_Language_Queries as text input
2. WHEN a Natural_Language_Query is submitted, THE Chat_Interface SHALL display the query in the conversation history
3. THE Chat_Interface SHALL send the Natural_Language_Query to the API_Server for processing
4. THE Chat_Interface SHALL display Query_Responses in the conversation history with formatted results
5. THE Chat_Interface SHALL maintain conversation context for follow-up questions
6. THE Chat_Interface SHALL display loading indicators while queries are being processed
7. WHEN an error occurs, THE Chat_Interface SHALL display user-friendly error messages

### Requirement 5: LLM-Powered Query Translation

**User Story:** As a system developer, I want to translate natural language to Cypher queries using an LLM, so that users can query without technical knowledge.

#### Acceptance Criteria

1. WHEN the API_Server receives a Natural_Language_Query, THE Query_Translator SHALL send the query to the LLM_Provider with graph schema context
2. THE Query_Translator SHALL include the Graph_Schema definition in the LLM prompt
3. THE Query_Translator SHALL include example Natural_Language_Query to Cypher_Query mappings in the LLM prompt
4. WHEN the LLM_Provider returns a response, THE Query_Translator SHALL extract the Cypher_Query from the response
5. THE Query_Translator SHALL validate that the extracted Cypher_Query contains valid Cypher syntax
6. IF the LLM_Provider returns an invalid response, THEN THE Query_Translator SHALL retry up to 2 additional times
7. IF all retry attempts fail, THEN THE Query_Translator SHALL return an error indicating translation failure

### Requirement 6: Query Execution and Response Generation

**User Story:** As a business analyst, I want my natural language questions answered with actual data, so that I can make informed decisions.

#### Acceptance Criteria

1. WHEN a valid Cypher_Query is generated, THE API_Server SHALL execute the query against the Graph_Database
2. THE API_Server SHALL transform query results into structured Query_Response format
3. WHEN query execution completes within 5 seconds, THE API_Server SHALL return the Query_Response to the Web_Client
4. THE API_Server SHALL format Query_Response data as JSON with clear field labels
5. WHEN a query returns no results, THE API_Server SHALL return an empty result set with appropriate messaging
6. IF query execution fails, THEN THE API_Server SHALL return an error message with failure details
7. IF query execution exceeds 30 seconds, THEN THE API_Server SHALL terminate the query and return a timeout error

### Requirement 7: Domain-Specific Query Guardrails

**User Story:** As a system administrator, I want to restrict queries to the business data domain, so that the system is not misused for unrelated purposes.

#### Acceptance Criteria

1. WHEN a Natural_Language_Query is received, THE Guardrail_System SHALL analyze the query intent before translation
2. THE Guardrail_System SHALL classify queries as in-domain if they reference Business_Entities or business processes
3. THE Guardrail_System SHALL classify queries as out-of-domain if they request general knowledge, personal advice, or unrelated topics
4. WHEN a query is classified as out-of-domain, THE Guardrail_System SHALL reject the query before LLM translation
5. WHEN a query is rejected, THE API_Server SHALL return a message explaining the domain restriction
6. THE Guardrail_System SHALL allow queries about Orders, Deliveries, Invoices, Payments, Customers, Products, and Addresses
7. THE Guardrail_System SHALL reject queries about topics unrelated to business intelligence or the dataset

### Requirement 8: Product Analysis Queries

**User Story:** As a business analyst, I want to identify which products are associated with the most billing documents, so that I can understand product performance.

#### Acceptance Criteria

1. WHEN a user asks about products with highest billing document counts, THE Query_Translator SHALL generate a Cypher_Query aggregating billing documents per product
2. THE API_Server SHALL execute the query and return products ranked by billing document count
3. THE Query_Response SHALL include product_id, product_name, and billing_document_count for each product
4. THE Query_Response SHALL sort results in descending order by billing_document_count
5. THE Query_Response SHALL limit results to the top 20 products by default

### Requirement 9: Flow Tracing Queries

**User Story:** As a business analyst, I want to trace the complete flow of a billing document, so that I can understand the end-to-end process.

#### Acceptance Criteria

1. WHEN a user requests a flow trace for a specific billing document, THE Query_Translator SHALL generate a Cypher_Query traversing all related entities
2. THE API_Server SHALL execute the query and return the complete Flow_Trace
3. THE Query_Response SHALL include all nodes in the path: Order → Delivery → Invoice → Payment
4. THE Query_Response SHALL include timestamps for each stage in the flow
5. THE Query_Response SHALL include status information for each entity in the flow
6. WHEN a flow is incomplete, THE Query_Response SHALL indicate which stages are missing

### Requirement 10: Broken Flow Detection

**User Story:** As a business analyst, I want to identify sales orders with incomplete flows, so that I can address process bottlenecks.

#### Acceptance Criteria

1. WHEN a user asks about broken or incomplete flows, THE Query_Translator SHALL generate a Cypher_Query identifying orders missing expected downstream entities
2. THE API_Server SHALL identify orders that have deliveries but no invoices
3. THE API_Server SHALL identify orders that have invoices but no payments
4. THE API_Server SHALL identify orders that have no deliveries after 7 days
5. THE Query_Response SHALL include order_id, order_date, current_status, and missing_stage for each broken flow
6. THE Query_Response SHALL categorize broken flows by type: delivered_not_billed, billed_not_paid, not_delivered

### Requirement 11: API Endpoint Structure

**User Story:** As a frontend developer, I want well-defined API endpoints, so that I can integrate the Web_Client with the API_Server.

#### Acceptance Criteria

1. THE API_Server SHALL expose a POST /api/query endpoint accepting Natural_Language_Queries
2. THE API_Server SHALL expose a GET /api/graph endpoint returning graph data for visualization
3. THE API_Server SHALL expose a POST /api/import endpoint accepting business data files
4. THE API_Server SHALL expose a GET /api/schema endpoint returning the Graph_Schema definition
5. THE API_Server SHALL expose a GET /api/health endpoint returning service status
6. THE API_Server SHALL return responses with appropriate HTTP status codes: 200 for success, 400 for client errors, 500 for server errors
7. THE API_Server SHALL include CORS headers allowing requests from the Web_Client origin

### Requirement 12: Query Translation Visibility (Optional)

**User Story:** As a power user, I want to see the generated Cypher query, so that I can understand how my question was translated.

#### Acceptance Criteria

1. WHERE translation visibility is enabled, THE API_Server SHALL include the generated Cypher_Query in the Query_Response
2. WHERE translation visibility is enabled, THE Web_Client SHALL display the Cypher_Query in an expandable section
3. WHERE translation visibility is enabled, THE Web_Client SHALL syntax-highlight the Cypher_Query for readability

### Requirement 13: Response Node Highlighting (Optional)

**User Story:** As a business analyst, I want nodes mentioned in query responses to be highlighted in the graph, so that I can visually locate relevant entities.

#### Acceptance Criteria

1. WHERE node highlighting is enabled, THE API_Server SHALL include node identifiers in the Query_Response
2. WHERE node highlighting is enabled, THE Web_Client SHALL extract node identifiers from the Query_Response
3. WHERE node highlighting is enabled, THE Graph_Visualizer SHALL apply visual highlighting to referenced nodes
4. WHERE node highlighting is enabled, THE Graph_Visualizer SHALL use distinct colors or borders for highlighted nodes

### Requirement 14: Streaming LLM Responses (Optional)

**User Story:** As a user, I want to see query responses appear progressively, so that I receive faster feedback for long responses.

#### Acceptance Criteria

1. WHERE streaming is enabled, THE API_Server SHALL establish a server-sent events connection for query responses
2. WHERE streaming is enabled, THE Query_Translator SHALL stream tokens from the LLM_Provider as they are generated
3. WHERE streaming is enabled, THE Chat_Interface SHALL display response tokens incrementally as they arrive
4. WHERE streaming is enabled, THE Chat_Interface SHALL indicate when streaming is complete

### Requirement 15: Configuration and Deployment

**User Story:** As a system administrator, I want clear configuration and deployment instructions, so that I can set up the system easily.

#### Acceptance Criteria

1. THE system SHALL include a README file documenting installation steps
2. THE README SHALL document required environment variables: Neo4j connection string, LLM API key, CORS origins
3. THE README SHALL document design decisions for graph modeling approach
4. THE README SHALL document the LLM prompting strategy for query translation
5. THE README SHALL document the guardrail implementation approach
6. THE system SHALL include a requirements.txt file listing Python dependencies
7. THE system SHALL include a package.json file listing JavaScript dependencies
8. THE system SHALL include example data files for testing the import functionality
