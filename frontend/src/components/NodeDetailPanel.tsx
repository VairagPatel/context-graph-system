import React from 'react';
import { Node, Edge } from '../types';

interface NodeDetailPanelProps {
  selectedItem: Node | Edge | null;
  onClose: () => void;
}

/**
 * NodeDetailPanel Component
 * 
 * Displays detailed information about a selected node or edge in a sidebar overlay.
 * Validates Requirements 3.3 and 3.4:
 * - 3.3: Display node properties when a node is clicked
 * - 3.4: Display relationship type and properties when an edge is clicked
 */
export const NodeDetailPanel: React.FC<NodeDetailPanelProps> = ({
  selectedItem,
  onClose,
}) => {
  if (!selectedItem) return null;

  // Type guard to determine if item is a Node or Edge
  const isNode = (item: Node | Edge): item is Node => {
    return 'data' in item && 'position' in item;
  };

  const isEdge = (item: Node | Edge): item is Edge => {
    return 'source' in item && 'target' in item;
  };

  const renderNodeDetails = (node: Node) => {
    const properties = node.data.properties || {};
    const propertyEntries = Object.entries(properties);

    return (
      <>
        {/* Entity Type Header */}
        <div className="mb-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-100 shadow-sm">
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center shadow-md">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <div>
              <p className="text-xs font-medium text-blue-600 uppercase tracking-wider">Entity Type</p>
              <h2 className="text-2xl font-bold text-gray-900">{node.type}</h2>
            </div>
          </div>
          <p className="text-sm text-gray-700 font-medium mt-2">{node.data.label}</p>
        </div>

        {/* Properties Section */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-4 flex items-center space-x-2">
            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>Properties</span>
          </h3>
          {propertyEntries.length > 0 ? (
            <div className="space-y-3">
              {propertyEntries.map(([key, value]) => (
                <div key={key} className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200">
                  <dt className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">
                    {key}
                  </dt>
                  <dd className="text-sm text-gray-900 font-medium break-words">
                    {formatPropertyValue(value)}
                  </dd>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-6 text-center border border-gray-200">
              <svg className="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
              <p className="text-sm text-gray-500 italic">No properties available</p>
            </div>
          )}
        </div>
      </>
    );
  };

  const renderEdgeDetails = (edge: Edge) => {
    return (
      <>
        {/* Relationship Type Header */}
        <div className="mb-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-5 border border-purple-100 shadow-sm">
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center shadow-md">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
            </div>
            <div>
              <p className="text-xs font-medium text-purple-600 uppercase tracking-wider">Relationship</p>
              <h2 className="text-2xl font-bold text-gray-900">{edge.type}</h2>
            </div>
          </div>
          <p className="text-sm text-gray-700 font-medium mt-2">{edge.label}</p>
        </div>

        {/* Connection Info */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-4 flex items-center space-x-2">
            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
            <span>Connection</span>
          </h3>
          <div className="space-y-3">
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200 hover:border-green-300 transition-colors duration-200">
              <dt className="text-xs font-semibold text-green-700 uppercase tracking-wide mb-1 flex items-center space-x-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                <span>Source</span>
              </dt>
              <dd className="text-sm text-gray-900 font-medium break-words">{edge.source}</dd>
            </div>
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200 hover:border-blue-300 transition-colors duration-200">
              <dt className="text-xs font-semibold text-blue-700 uppercase tracking-wide mb-1 flex items-center space-x-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
                <span>Target</span>
              </dt>
              <dd className="text-sm text-gray-900 font-medium break-words">{edge.target}</dd>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-gray-300 transition-colors duration-200">
              <dt className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">
                Label
              </dt>
              <dd className="text-sm text-gray-900 font-medium break-words">{edge.label}</dd>
            </div>
          </div>
        </div>
      </>
    );
  };

  return (
    <>
      {/* Overlay backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-40 z-40 backdrop-blur-sm transition-opacity duration-300"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Sidebar panel */}
      <div className="fixed top-0 right-0 h-full w-96 bg-white shadow-2xl z-50 flex flex-col animate-slide-in-right">
        {/* Header with close button */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center shadow-sm">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h1 className="text-lg font-semibold text-gray-900">Details</h1>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 active:bg-gray-200 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Close panel"
          >
            <svg
              className="w-5 h-5 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content area */}
        <div className="flex-1 overflow-y-auto px-6 py-6 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
          {isNode(selectedItem) && renderNodeDetails(selectedItem)}
          {isEdge(selectedItem) && renderEdgeDetails(selectedItem)}
        </div>
      </div>
    </>
  );
};

// Helper function to format property values
const formatPropertyValue = (value: any): string => {
  if (value === null || value === undefined) {
    return '-';
  }
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No';
  }
  if (typeof value === 'object') {
    if (value instanceof Date) {
      return value.toLocaleString();
    }
    return JSON.stringify(value, null, 2);
  }
  if (typeof value === 'number') {
    return value.toLocaleString();
  }
  return String(value);
};
