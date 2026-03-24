import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node as FlowNode,
  Edge as FlowEdge,
  Controls,
  MiniMap,
  Background,
  BackgroundVariant,
  NodeMouseHandler,
  EdgeMouseHandler,
  ConnectionLineType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Node, Edge } from '../types';

interface GraphVisualizerProps {
  nodes: Node[];
  edges: Edge[];
  onNodeClick: (node: Node) => void;
  onEdgeClick: (edge: Edge) => void;
  highlightedNodeIds?: string[];
}

// Entity type to color mapping
const NODE_COLORS: Record<string, string> = {
  Order: '#3b82f6', // blue
  Delivery: '#22c55e', // green
  Invoice: '#f97316', // orange
  Payment: '#a855f7', // purple
  Customer: '#ec4899', // pink
  Product: '#eab308', // yellow
  Address: '#6b7280', // gray
  Plant: '#14b8a6', // teal
  SalesOrder: '#3b82f6', // blue
  BillingDocument: '#f97316', // orange
  BusinessPartner: '#ec4899', // pink
};

const GraphVisualizer: React.FC<GraphVisualizerProps> = ({
  nodes,
  edges,
  onNodeClick,
  onEdgeClick,
  highlightedNodeIds = [],
}) => {
  // Convert our Node/Edge types to React Flow format with styling
  const flowNodes: FlowNode[] = useMemo(() => {
    if (!nodes || nodes.length === 0) return [];
    
    return nodes.map((node, index) => {
      const isHighlighted = highlightedNodeIds.includes(node.id);
      const baseColor = NODE_COLORS[node.type] || '#6b7280';

      // Ensure position is always defined with fallback
      const position = node.position || { x: (index % 10) * 200, y: Math.floor(index / 10) * 150 };

      return {
        id: node.id,
        type: 'default',
        data: {
          label: node.data?.label || node.id,
          ...node.data,
        },
        position: position,
        style: {
          background: baseColor,
          color: '#ffffff',
          border: isHighlighted ? '3px solid #fbbf24' : '2px solid #1f2937',
          borderRadius: '8px',
          padding: '10px',
          fontSize: '12px',
          fontWeight: isHighlighted ? 'bold' : 'normal',
          boxShadow: isHighlighted
            ? '0 0 20px rgba(251, 191, 36, 0.6)'
            : '0 2px 4px rgba(0, 0, 0, 0.1)',
          minWidth: '120px',
          textAlign: 'center',
        },
      };
    });
  }, [nodes, highlightedNodeIds]);

  const flowEdges: FlowEdge[] = useMemo(() => {
    if (!edges || edges.length === 0) return [];
    
    return edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: ConnectionLineType.SmoothStep,
      label: edge.label,
      animated: false,
      style: {
        stroke: '#64748b',
        strokeWidth: 2,
      },
      labelStyle: {
        fontSize: '10px',
        fill: '#475569',
        fontWeight: 500,
      },
      labelBgStyle: {
        fill: '#ffffff',
        fillOpacity: 0.8,
      },
    }));
  }, [edges]);

  // Handle node click
  const handleNodeClick: NodeMouseHandler = useCallback(
    (event, node) => {
      const originalNode = nodes.find((n) => n.id === node.id);
      if (originalNode) {
        onNodeClick(originalNode);
      }
    },
    [nodes, onNodeClick]
  );

  // Handle edge click
  const handleEdgeClick: EdgeMouseHandler = useCallback(
    (event, edge) => {
      const originalEdge = edges.find((e) => e.id === edge.id);
      if (originalEdge) {
        onEdgeClick(originalEdge);
      }
    },
    [edges, onEdgeClick]
  );

  return (
    <div className="relative w-full h-full bg-gradient-to-br from-gray-50 to-gray-100">
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        onNodeClick={handleNodeClick}
        onEdgeClick={handleEdgeClick}
        fitView
        attributionPosition="bottom-left"
        minZoom={0.1}
        maxZoom={2}
      >
        <Controls 
          className="bg-white shadow-lg rounded-lg border border-gray-200 overflow-hidden"
          showInteractive={false}
        />
        <MiniMap
          className="bg-white shadow-lg rounded-lg border border-gray-200 overflow-hidden"
          nodeColor={(node) => {
            const originalNode = nodes.find((n) => n.id === node.id);
            return originalNode ? NODE_COLORS[originalNode.type] || '#6b7280' : '#6b7280';
          }}
          nodeStrokeWidth={3}
          zoomable
          pannable
          maskColor="rgba(0, 0, 0, 0.1)"
        />
        <Background 
          variant={BackgroundVariant.Dots} 
          gap={16} 
          size={1} 
          color="#d1d5db"
        />
      </ReactFlow>
      
      {/* Legend */}
      <div className="absolute top-4 left-4 bg-white shadow-lg rounded-lg border border-gray-200 p-4 max-w-xs z-10">
        <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center space-x-2">
          <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
          </svg>
          <span>Entity Types</span>
        </h3>
        <div className="space-y-2">
          {Object.entries(NODE_COLORS).map(([type, color]) => (
            <div key={type} className="flex items-center space-x-2 text-xs">
              <div 
                className="w-4 h-4 rounded shadow-sm border border-gray-300"
                style={{ backgroundColor: color }}
                aria-hidden="true"
              />
              <span className="text-gray-700 font-medium">{type}</span>
            </div>
          ))}
        </div>
      </div>
      
      {/* Node count indicator */}
      {nodes.length > 0 && (
        <div className="absolute bottom-4 left-4 bg-white shadow-lg rounded-lg border border-gray-200 px-4 py-2 z-10">
          <div className="flex items-center space-x-2 text-sm">
            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span className="text-gray-700 font-medium">
              {nodes.length} node{nodes.length !== 1 ? 's' : ''}, {edges.length} edge{edges.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default GraphVisualizer;
