import React, { useState, useRef, useEffect } from 'react';
import { Message, QueryResponse } from '../types';

interface ChatInterfaceProps {
  onQuerySubmit: (query: string) => Promise<QueryResponse>;
  conversationHistory: Message[];
  loading: boolean;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onQuerySubmit,
  conversationHistory,
  loading,
}) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversationHistory]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || loading) return;

    const query = inputValue.trim();
    setInputValue('');
    await onQuerySubmit(query);
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Message History */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
        {conversationHistory.length === 0 && (
          <div className="text-center text-gray-500 mt-12 px-4">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Welcome to Graph Query System</h2>
            <p className="text-sm text-gray-600 max-w-md mx-auto">Ask questions about your business data in natural language. Try asking about orders, deliveries, invoices, or product analytics.</p>
          </div>
        )}

        {conversationHistory.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {loading && (
          <div className="flex items-start space-x-3 animate-fade-in">
            <div className="flex-shrink-0 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-400 border-t-transparent" role="status" aria-label="Loading"></div>
            </div>
            <div className="flex-1 bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="border-t border-gray-200 bg-white p-4 shadow-lg">
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask a question about your data..."
            disabled={loading}
            aria-label="Query input"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed transition-all duration-200 placeholder-gray-400"
          />
          <button
            type="submit"
            disabled={loading || !inputValue.trim()}
            aria-label="Submit query"
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed disabled:hover:bg-gray-300 transition-all duration-200 shadow-sm hover:shadow-md active:scale-95"
          >
            {loading ? (
              <span className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" role="status" aria-label="Sending"></div>
                <span>Sending</span>
              </span>
            ) : (
              'Send'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const [showCypher, setShowCypher] = useState(false);
  const isUser = message.type === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
      <div className={`max-w-3xl ${isUser ? 'w-auto' : 'w-full'}`}>
        {/* Avatar for assistant messages */}
        {!isUser && (
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center shadow-sm">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div className="flex-1">
              {/* Message Content */}
              <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow duration-200">
                <p className="whitespace-pre-wrap text-gray-900">{message.content}</p>
                
                {/* Timestamp */}
                <p className="text-xs mt-2 text-gray-500">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>

        {/* Query Results Table */}
        {!isUser && message.data && message.data.length > 0 && (
          <div className="mt-3 bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                  <tr>
                    {Object.keys(message.data[0]).map((key) => (
                      <th
                        key={key}
                        className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                      >
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {message.data.map((row, idx) => (
                    <tr key={idx} className="hover:bg-blue-50 transition-colors duration-150">
                      {Object.values(row).map((value, cellIdx) => (
                        <td key={cellIdx} className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap">
                          {formatCellValue(value)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="px-4 py-2 bg-gradient-to-r from-gray-50 to-gray-100 text-xs text-gray-600 border-t border-gray-200 flex items-center space-x-2">
              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>{message.data.length} result{message.data.length !== 1 ? 's' : ''}</span>
            </div>
          </div>
        )}

        {/* Empty Results Message */}
        {!isUser && message.data && message.data.length === 0 && !message.error && (
          <div className="mt-3 bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-start space-x-3 shadow-sm">
            <svg className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-amber-900">No results found</p>
              <p className="text-sm text-amber-700 mt-1">Try rephrasing your query or asking about different data.</p>
            </div>
          </div>
        )}

        {/* Error Message Display */}
        {!isUser && message.error && (
          <div className="mt-3 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3 shadow-sm">
            <svg className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-semibold text-red-900">Error</p>
              <p className="text-sm text-red-700 mt-1">{message.error}</p>
            </div>
          </div>
        )}

        {/* Cypher Query Display (Optional) */}
        {!isUser && message.cypher && (
          <div className="mt-3">
            <button
              onClick={() => setShowCypher(!showCypher)}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center space-x-2 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded px-2 py-1"
              aria-expanded={showCypher}
              aria-label="Toggle Cypher query display"
            >
              <svg className={`w-4 h-4 transition-transform duration-200 ${showCypher ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <span>Generated Cypher Query</span>
            </button>
            {showCypher && (
              <div className="mt-2 bg-gray-900 text-gray-100 rounded-lg p-4 overflow-x-auto shadow-lg animate-fade-in">
                <pre className="text-sm font-mono leading-relaxed">{message.cypher}</pre>
              </div>
            )}
          </div>
        )}
            </div>
          </div>
        )}
        
        {/* User message bubble */}
        {isUser && (
          <div className="flex items-start space-x-3 justify-end">
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-lg p-4 shadow-md hover:shadow-lg transition-shadow duration-200">
              <p className="whitespace-pre-wrap">{message.content}</p>
              
              {/* Timestamp */}
              <p className="text-xs mt-2 text-blue-100">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
            <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-gray-600 to-gray-700 rounded-full flex items-center justify-center shadow-sm">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper function to format cell values
const formatCellValue = (value: any): string => {
  if (value === null || value === undefined) {
    return '-';
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  if (typeof value === 'number') {
    return value.toLocaleString();
  }
  return String(value);
};
