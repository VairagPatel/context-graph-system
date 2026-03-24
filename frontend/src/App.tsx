import React, { useState, useEffect } from 'react';
import { ChatInterface } from './components/ChatInterface';
import GraphVisualizer from './components/GraphVisualizer';
import { NodeDetailPanel } from './components/NodeDetailPanel';
import { submitQuery, fetchGraphData } from './services/api';
import { Node, Edge, Message, QueryResponse, GraphData } from './types';

/**
 * Main App Component
 * 
 * Manages application state and coordinates between ChatInterface, 
 * GraphVisualizer, and NodeDetailPanel components.
 * 
 * Validates Requirements:
 * - 3.7: Fetch graph data from API and pass to visualizer
 * - 4.3: Send natural language queries to API
 * - 4.4: Display query responses in conversation history
 * - 13.1: Include node identifiers in query response
 * - 13.2: Extract node identifiers from query response
 * - 13.3: Apply visual highlighting to referenced nodes
 * - 13.4: Use distinct colors/borders for highlighted nodes
 */
function App() {
  // State management
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
  const [conversationHistory, setConversationHistory] = useState<Message[]>([]);
  const [selectedItem, setSelectedItem] = useState<Node | Edge | null>(null);
  const [loading, setLoading] = useState(false);
  const [highlightedNodeIds, setHighlightedNodeIds] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Fetch initial graph data on component mount
  useEffect(() => {
    const loadGraphData = async () => {
      try {
        const data = await fetchGraphData(100);
        setGraphData(data);
      } catch (err) {
        console.error('Failed to load graph data:', err);
        setError('Failed to load graph data. Please check your connection.');
      }
    };

    loadGraphData();
  }, []);

  /**
   * Handle query submission from ChatInterface
   * Sends query to API, updates conversation history, and highlights nodes
   */
  const handleQuerySubmit = async (query: string): Promise<QueryResponse> => {
    setLoading(true);
    setError(null);

    // Add user message to conversation
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: query,
      timestamp: new Date(),
    };
    setConversationHistory((prev) => [...prev, userMessage]);

    try {
      // Submit query to API
      const response = await submitQuery({
        query,
        include_cypher: true, // Request Cypher query for display
      });

      // Add assistant response to conversation
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        type: 'assistant',
        content: response.success
          ? 'Here are the results:'
          : response.error || 'An error occurred',
        timestamp: new Date(),
        cypher: response.cypher,
        data: response.data,
        error: response.error,
      };
      setConversationHistory((prev) => [...prev, assistantMessage]);

      // Highlight nodes mentioned in response (optional feature)
      if (response.node_ids && response.node_ids.length > 0) {
        setHighlightedNodeIds(response.node_ids);
      } else {
        setHighlightedNodeIds([]);
      }

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      
      // Add error message to conversation
      const errorAssistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your query.',
        timestamp: new Date(),
        error: errorMessage,
      };
      setConversationHistory((prev) => [...prev, errorAssistantMessage]);

      return {
        success: false,
        data: [],
        error: errorMessage,
      };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle node click from GraphVisualizer
   * Updates selectedItem state to display in NodeDetailPanel
   */
  const handleNodeClick = (node: Node) => {
    setSelectedItem(node);
  };

  /**
   * Handle edge click from GraphVisualizer
   * Updates selectedItem state to display in NodeDetailPanel
   */
  const handleEdgeClick = (edge: Edge) => {
    setSelectedItem(edge);
  };

  /**
   * Close NodeDetailPanel
   */
  const handleClosePanel = () => {
    setSelectedItem(null);
  };

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center shadow-md">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Graph Query System</h1>
              <p className="text-sm text-gray-600">
                Explore business data through interactive visualization and natural language queries
              </p>
            </div>
          </div>
          
          {/* Status indicator */}
          <div className="flex items-center space-x-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" aria-hidden="true"></div>
            <span className="text-xs font-medium text-green-700">Connected</span>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 px-6 py-3 flex items-center space-x-3 animate-fade-in">
          <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-red-800 font-medium">{error}</p>
        </div>
      )}

      {/* Main Content - Split View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Graph Visualization */}
        <div className="flex-1 bg-white border-r border-gray-200 shadow-sm relative">
          {graphData.nodes.length === 0 ? (
            <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
              <div className="text-center px-4">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-100 rounded-full mb-4">
                  <svg className="w-10 h-10 text-blue-600 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Loading Graph Data</h3>
                <p className="text-sm text-gray-600">Please wait while we fetch your data...</p>
              </div>
            </div>
          ) : (
            <GraphVisualizer
              nodes={graphData.nodes}
              edges={graphData.edges}
              onNodeClick={handleNodeClick}
              onEdgeClick={handleEdgeClick}
              highlightedNodeIds={highlightedNodeIds}
            />
          )}
        </div>

        {/* Right Panel - Chat Interface */}
        <div className="w-full md:w-1/3 md:min-w-[400px] md:max-w-[600px] shadow-lg">
          <ChatInterface
            onQuerySubmit={handleQuerySubmit}
            conversationHistory={conversationHistory}
            loading={loading}
          />
        </div>
      </div>

      {/* Node Detail Panel (Overlay) */}
      <NodeDetailPanel selectedItem={selectedItem} onClose={handleClosePanel} />
    </div>
  );
}

export default App;
