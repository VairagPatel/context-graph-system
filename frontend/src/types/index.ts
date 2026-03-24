/**
 * TypeScript type definitions for the Graph-Based Data Modeling and Query System
 * 
 * These interfaces define the data structures used throughout the frontend application
 * for graph visualization, API communication, and chat interface.
 */

/**
 * Represents a node in the graph visualization
 * Used by React Flow to render business entities
 */
export interface Node {
  id: string;
  type: string; // Entity type: Order, Delivery, Invoice, Payment, Customer, Product, Address
  data: {
    label: string;
    properties: Record<string, any>;
  };
  position: { x: number; y: number };
}

/**
 * Represents an edge (relationship) in the graph visualization
 * Used by React Flow to render connections between entities
 */
export interface Edge {
  id: string;
  source: string; // Source node ID
  target: string; // Target node ID
  type: string; // Relationship type
  label: string; // Display label for the edge
}

/**
 * Represents a message in the chat conversation
 * Used by ChatInterface to display conversation history
 */
export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  cypher?: string; // Optional generated Cypher query
  data?: any[]; // Optional query results
  error?: string; // Optional error message
}

/**
 * Request payload for natural language query endpoint
 * Sent to POST /api/query
 */
export interface QueryRequest {
  query: string;
  conversation_id?: string;
  include_cypher?: boolean;
}

/**
 * Response from natural language query endpoint
 * Received from POST /api/query
 */
export interface QueryResponse {
  success: boolean;
  data: Array<Record<string, any>>;
  cypher?: string;
  error?: string;
  node_ids?: string[];
}

/**
 * Graph data structure containing nodes and edges
 * Used for graph visualization and received from GET /api/graph
 */
export interface GraphData {
  nodes: Node[];
  edges: Edge[];
}
