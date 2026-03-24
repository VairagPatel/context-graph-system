# Implementation Plan: Graph-Based Data Modeling and Query System

## Overview

This implementation plan breaks down the Graph-Based Data Modeling and Query System into incremental coding tasks. The system consists of a Python FastAPI backend with Neo4j database integration, LLM-powered query translation, and a React frontend with interactive graph visualization. Tasks are organized to build core functionality first, then add advanced features, with testing integrated throughout.

## Tasks

- [x] 1. Set up project structure and configuration
  - Create backend directory structure (app/, app/services/, app/models/, app/api/)
  - Create frontend directory structure (src/, src/components/, src/services/, src/types/)
  - Create backend requirements.txt with dependencies: fastapi, uvicorn, neo4j, pydantic, httpx, python-multipart, python-dotenv
  - Create frontend package.json with dependencies: react, react-dom, vite, reactflow, axios, tailwindcss
  - Create .env.example files for both backend and frontend with required environment variables
  - Create README.md with setup instructions and architecture overview
  - _Requirements: 15.1, 15.2, 15.6, 15.7_

- [x] 2. Implement Neo4j service and database connectivity
  - [x] 2.1 Create Neo4jService class in app/services/neo4j_service.py
    - Implement __init__ with connection parameters (uri, user, password)
    - Implement execute_query method to run Cypher queries and return results
    - Implement health_check method to verify database connectivity
    - Implement create_node method for creating nodes with labels and properties
    - Implement create_relationship method for creating edges between nodes
    - Implement get_graph_data method to fetch nodes and edges for visualization
    - Add connection pooling and error handling
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 3.7_

  - [x] 2.2 Write unit tests for Neo4jService
    - Test connection establishment and health check
    - Test query execution with mock Neo4j driver
    - Test node and relationship creation
    - Test error handling for connection failures
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

- [x] 3. Implement data import service
  - [x] 3.1 Create DataImportService class in app/services/data_import.py
    - Implement __init__ accepting Neo4jService dependency
    - Implement import_file method to process CSV/JSON files
    - Implement _validate_data method to check required fields per entity type
    - Implement _infer_relationships method to create edges from foreign keys
    - Add support for all 7 entity types (Order, Delivery, Invoice, Payment, Customer, Product, Address)
    - Return ImportResult with nodes_created, relationships_created, and errors
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [x] 3.2 Write unit tests for DataImportService
    - Test CSV parsing and validation
    - Test JSON parsing and validation
    - Test relationship inference logic
    - Test error handling for invalid data
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 4. Implement guardrail system
  - [x] 4.1 Create GuardrailSystem class in app/services/guardrails.py
    - Implement classify_query method using keyword-based classification
    - Define in-domain keywords (order, delivery, invoice, payment, customer, product, address, billing, shipping, flow, trace)
    - Define out-of-domain keywords (weather, sports, news, personal, advice, general knowledge)
    - Return QueryClassification with is_valid and reason fields
    - Add logging for rejected queries
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

  - [x] 4.2 Write unit tests for GuardrailSystem
    - Test in-domain query classification (business entity queries)
    - Test out-of-domain query rejection (weather, sports, personal advice)
    - Test edge cases and ambiguous queries
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

- [x] 5. Implement LLM-powered query translator
  - [x] 5.1 Create QueryTranslator class in app/services/query_translator.py
    - Implement __init__ accepting llm_provider (groq or gemini), api_key, and schema
    - Implement translate method to convert natural language to Cypher
    - Implement _build_prompt method with schema context and few-shot examples
    - Add 8-10 example query translations covering common patterns (product analysis, flow tracing, broken flows)
    - Implement _validate_cypher method for basic syntax validation
    - Add retry logic (up to 2 retries) for LLM failures
    - Support both Groq and Gemini API formats
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

  - [x] 5.2 Write unit tests for QueryTranslator
    - Test prompt construction with schema and examples
    - Test Cypher validation logic
    - Test retry mechanism with mock LLM failures
    - Test both Groq and Gemini API integrations
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [x] 6. Checkpoint - Ensure all backend services are functional
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement API data models
  - [x] 7.1 Create Pydantic models in app/models/api_models.py
    - Create QueryRequest model (query, conversation_id, include_cypher)
    - Create QueryResponse model (success, data, cypher, error, node_ids)
    - Create ImportResponse model (success, nodes_created, relationships_created, errors)
    - Create GraphNode model (id, label, properties)
    - Create GraphEdge model (id, source, target, type, properties)
    - Create GraphData model (nodes, edges)
    - Create QueryClassification model (is_valid, reason)
    - Create TranslationResult model (cypher, success, error)
    - Create ImportResult model (success, nodes_created, relationships_created, errors)
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 8. Implement FastAPI endpoints
  - [x] 8.1 Create main FastAPI application in app/main.py
    - Initialize FastAPI app with CORS middleware
    - Initialize Neo4jService, GuardrailSystem, QueryTranslator, DataImportService
    - Implement POST /api/query endpoint
    - Implement GET /api/graph endpoint with limit parameter
    - Implement POST /api/import endpoint with file upload
    - Implement GET /api/schema endpoint
    - Implement GET /api/health endpoint
    - Add error handling and appropriate HTTP status codes (200, 400, 500)
    - _Requirements: 4.1, 4.2, 4.3, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_

  - [x] 8.2 Write integration tests for API endpoints
    - Test /api/query endpoint with valid and invalid queries
    - Test /api/graph endpoint with different limit values
    - Test /api/import endpoint with CSV and JSON files
    - Test /api/schema and /api/health endpoints
    - Test error handling and status codes
    - _Requirements: 4.1, 4.2, 4.3, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_

- [x] 9. Checkpoint - Verify backend API is fully functional
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Set up frontend project structure
  - [x] 10.1 Initialize Vite React TypeScript project
    - Run vite create command for React TypeScript template
    - Configure TailwindCSS with postcss and tailwind.config.js
    - Create src/types/ directory for TypeScript interfaces
    - Create src/services/ directory for API client
    - Create src/components/ directory for React components
    - Configure environment variables in .env file (VITE_API_URL)
    - _Requirements: 15.7_

- [x] 11. Implement TypeScript types and API client
  - [x] 11.1 Create TypeScript interfaces in src/types/index.ts
    - Define Node interface (id, type, data with label and properties, position)
    - Define Edge interface (id, source, target, type, label)
    - Define Message interface (id, type, content, timestamp, cypher, data)
    - Define QueryRequest interface (query, conversation_id, include_cypher)
    - Define QueryResponse interface (success, data, cypher, error, node_ids)
    - Define GraphData interface (nodes, edges)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [x] 11.2 Create API client in src/services/api.ts
    - Configure axios instance with base URL from environment
    - Implement submitQuery function calling POST /api/query
    - Implement fetchGraphData function calling GET /api/graph
    - Implement uploadDataFile function calling POST /api/import
    - Implement fetchSchema function calling GET /api/schema
    - Add error handling and response transformation
    - _Requirements: 4.3, 3.7, 11.1, 11.2, 11.3, 11.4_

- [x] 12. Implement Chat Interface component
  - [x] 12.1 Create ChatInterface component in src/components/ChatInterface.tsx
    - Accept onQuerySubmit, conversationHistory, and loading props
    - Render message history with user and assistant messages
    - Implement text input with submit button
    - Display loading indicators during query processing
    - Format query results as tables for structured data
    - Add expandable section for Cypher query display (optional)
    - Display error messages with user-friendly formatting
    - Auto-scroll to latest message
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 12.1, 12.2, 12.3_

  - [x] 12.2 Write component tests for ChatInterface
    - Test message rendering for user and assistant
    - Test query submission and loading states
    - Test error message display
    - Test Cypher query expansion
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [x] 13. Implement Graph Visualizer component
  - [x] 13.1 Create GraphVisualizer component in src/components/GraphVisualizer.tsx
    - Accept nodes, edges, onNodeClick, onEdgeClick, and highlightedNodeIds props
    - Configure React Flow with controls, minimap, and background
    - Define custom node styles with distinct colors per entity type (Order: blue, Delivery: green, Invoice: orange, Payment: purple, Customer: pink, Product: yellow, Address: gray)
    - Implement node click handler to trigger onNodeClick callback
    - Implement edge click handler to trigger onEdgeClick callback
    - Apply highlighted styling to nodes in highlightedNodeIds array
    - Configure automatic layout using force-directed algorithm for large graphs
    - Add pan, zoom, and drag interactions
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.8, 13.2, 13.3, 13.4_

  - [x] 13.2 Write component tests for GraphVisualizer
    - Test node rendering with correct colors
    - Test edge rendering with labels
    - Test node click interactions
    - Test highlighted node styling
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 13.2, 13.3, 13.4_

- [x] 14. Implement Node Detail Panel component
  - [x] 14.1 Create NodeDetailPanel component in src/components/NodeDetailPanel.tsx
    - Accept selectedItem (Node or Edge) and onClose props
    - Display entity type header
    - Render property list as key-value pairs
    - Add close button to dismiss panel
    - Style panel as sidebar overlay
    - _Requirements: 3.3, 3.4_

- [x] 15. Implement main App component and state management
  - [x] 15.1 Create App component in src/App.tsx
    - Initialize state for graphData, conversationHistory, selectedNode, and loading
    - Implement handleQuerySubmit function calling API client and updating conversation history
    - Implement handleNodeClick function to update selectedNode state
    - Fetch initial graph data on component mount
    - Pass state and handlers to ChatInterface, GraphVisualizer, and NodeDetailPanel
    - Implement layout with split view (graph on left, chat on right)
    - Add optional node highlighting based on query response node_ids
    - _Requirements: 3.7, 4.3, 4.4, 13.1, 13.2, 13.3, 13.4_

  - [x] 15.2 Write integration tests for App component
    - Test initial graph data loading
    - Test query submission flow
    - Test node selection and detail panel display
    - Test error handling
    - _Requirements: 3.7, 4.3, 4.4_

- [x] 16. Checkpoint - Verify frontend is fully functional
  - Ensure all tests pass, ask the user if questions arise.

- [x] 17. Create example data files for testing
  - [x] 17.1 Create sample data files in data/ directory
    - Create orders.csv with 20 sample orders
    - Create deliveries.csv with 18 sample deliveries (2 orders without deliveries)
    - Create invoices.csv with 15 sample invoices (3 orders without invoices)
    - Create payments.csv with 12 sample payments (3 invoices without payments)
    - Create customers.csv with 10 sample customers
    - Create products.csv with 8 sample products
    - Create addresses.csv with 10 sample addresses
    - Ensure foreign key relationships are valid across files
    - Include examples of broken flows (delivered but not billed, billed but not paid)
    - _Requirements: 15.8, 9.6, 10.2, 10.3, 10.4, 10.6_

- [x] 18. Implement product analysis query support
  - [x] 18.1 Add product analysis examples to QueryTranslator prompt
    - Add example: "Show me the top 10 products by number of orders" → Cypher query
    - Add example: "Which products have the most invoices?" → Cypher query
    - Add example: "List products by billing document count" → Cypher query
    - Ensure generated queries aggregate by product and sort by count
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 19. Implement flow tracing query support
  - [x] 19.1 Add flow tracing examples to QueryTranslator prompt
    - Add example: "Trace the complete flow for order 12345" → Cypher query with path traversal
    - Add example: "Show me the full process for invoice INV-001" → Cypher query
    - Ensure generated queries return all related entities (Order, Delivery, Invoice, Payment)
    - Ensure queries include timestamps and status fields
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 20. Implement broken flow detection query support
  - [x] 20.1 Add broken flow detection examples to QueryTranslator prompt
    - Add example: "Find orders that have been delivered but not invoiced" → Cypher query with NOT EXISTS
    - Add example: "Show me invoices without payments" → Cypher query
    - Add example: "Which orders haven't been delivered after 7 days?" → Cypher query with date comparison
    - Ensure generated queries categorize broken flows by type
    - Ensure queries return order_id, order_date, current_status, and missing_stage
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [x] 21. Add styling and UI polish
  - [x] 21.1 Apply TailwindCSS styling to all components
    - Style ChatInterface with modern chat UI design
    - Style GraphVisualizer with clean controls and minimap
    - Style NodeDetailPanel with card-based layout
    - Add responsive layout for different screen sizes
    - Add loading spinners and skeleton screens
    - Add hover effects and transitions
    - Ensure accessibility (ARIA labels, keyboard navigation)
    - _Requirements: 3.1, 3.2, 4.1, 4.2, 4.6_

- [x] 22. Create deployment configuration
  - [x] 22.1 Create backend deployment configuration
    - Create Dockerfile for FastAPI backend
    - Create render.yaml or railway.json for deployment
    - Document environment variable configuration
    - Add health check endpoint verification
    - _Requirements: 15.1, 15.2_

  - [x] 22.2 Create frontend deployment configuration
    - Configure Vite build settings for production
    - Create vercel.json for Vercel deployment
    - Document environment variable configuration for API URL
    - _Requirements: 15.1, 15.2_

- [x] 23. Update README with comprehensive documentation
  - [x] 23.1 Document setup and deployment instructions
    - Add prerequisites (Python 3.11+, Node.js 18+, Neo4j Aura account)
    - Add backend setup steps (install dependencies, configure .env, run server)
    - Add frontend setup steps (install dependencies, configure .env, run dev server)
    - Add deployment instructions for Render/Railway and Vercel
    - Document Neo4j Aura setup and connection string format
    - Document LLM API key setup for Groq or Gemini
    - _Requirements: 15.1, 15.2_

  - [x] 23.2 Document design decisions and architecture
    - Explain graph modeling approach and schema design
    - Explain LLM prompting strategy with few-shot examples
    - Explain guardrail implementation using keyword classification
    - Add architecture diagram
    - Add API endpoint documentation
    - _Requirements: 15.3, 15.4, 15.5_

- [x] 24. Final checkpoint - End-to-end verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Backend tasks (1-9) should be completed before frontend tasks (10-16)
- Example data files (17) can be created in parallel with development
- Query support tasks (18-20) enhance the LLM prompt and can be done incrementally
- Deployment configuration (22) and documentation (23) finalize the project
