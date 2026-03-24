/**
 * API Client for Graph-Based Data Modeling and Query System
 * 
 * This module provides functions to communicate with the FastAPI backend.
 * It uses axios for HTTP requests and handles error transformation.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { QueryRequest, QueryResponse, GraphData } from '../types';

/**
 * Configure axios instance with base URL from environment
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

/**
 * Error handler to transform axios errors into user-friendly messages
 */
const handleApiError = (error: AxiosError): never => {
  if (error.response) {
    // Server responded with error status
    const message = (error.response.data as any)?.error || error.response.statusText;
    throw new Error(`API Error: ${message}`);
  } else if (error.request) {
    // Request made but no response received
    throw new Error('Network Error: Unable to reach the server');
  } else {
    // Error in request setup
    throw new Error(`Request Error: ${error.message}`);
  }
};

/**
 * Submit a natural language query to the backend
 * 
 * @param request - Query request containing the natural language query
 * @returns Promise resolving to query response with results
 */
export const submitQuery = async (request: QueryRequest): Promise<QueryResponse> => {
  try {
    const response = await apiClient.post<QueryResponse>('/api/query', request);
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
};

/**
 * Fetch graph data for visualization
 * 
 * @param limit - Maximum number of nodes to fetch (default: 100)
 * @returns Promise resolving to graph data with nodes and edges
 */
export const fetchGraphData = async (limit: number = 100): Promise<GraphData> => {
  try {
    const response = await apiClient.get<{
      nodes: Array<{ id: string; label: string; properties: Record<string, any> }>;
      edges: Array<{ id: string; source: string; target: string; type: string; properties: Record<string, any> }>;
    }>('/api/graph', {
      params: { limit },
    });
    
    console.log('API Response:', response.data);
    
    // Transform API response to frontend format with proper positioning
    const nodes = response.data.nodes.map((node, index) => {
      // Create a grid layout for nodes
      const gridSize = Math.ceil(Math.sqrt(response.data.nodes.length));
      const row = Math.floor(index / gridSize);
      const col = index % gridSize;
      
      const transformedNode = {
        id: node.id,
        type: node.label,
        data: {
          label: node.properties.plantName || node.properties.name || node.properties.plant || node.properties.product || node.label,
          properties: node.properties,
        },
        position: {
          x: col * 250,
          y: row * 150,
        },
      };
      
      console.log('Transformed node:', transformedNode);
      return transformedNode;
    });
    
    const edges = response.data.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: edge.type,
      label: edge.type,
    }));
    
    console.log('Final transformed data:', { nodes, edges });
    return { nodes, edges };
  } catch (error) {
    console.error('Error fetching graph data:', error);
    return handleApiError(error as AxiosError);
  }
};

/**
 * Upload a data file for import into the graph database
 * 
 * @param file - File object containing CSV or JSON data
 * @returns Promise resolving to import response with statistics
 */
export const uploadDataFile = async (file: File): Promise<{
  success: boolean;
  nodes_created: number;
  relationships_created: number;
  errors?: string[];
}> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/api/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
};

/**
 * Fetch the graph schema definition
 * 
 * @returns Promise resolving to schema with node types and relationship types
 */
export const fetchSchema = async (): Promise<{
  node_types: Array<{
    label: string;
    properties: string[];
  }>;
  relationship_types: string[];
}> => {
  try {
    const response = await apiClient.get('/api/schema');
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
};

/**
 * Check the health status of the backend API
 * 
 * @returns Promise resolving to health status
 */
export const checkHealth = async (): Promise<{
  status: string;
  neo4j_connected: boolean;
  llm_provider: string;
}> => {
  try {
    const response = await apiClient.get('/api/health');
    return response.data;
  } catch (error) {
    return handleApiError(error as AxiosError);
  }
};
