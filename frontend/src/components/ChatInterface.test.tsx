/**
 * Component tests for ChatInterface
 * 
 * **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7**
 * 
 * Tests cover:
 * - Message rendering for user and assistant messages
 * - Query submission and loading states
 * - Error message display
 * - Cypher query expansion
 * - Query results table rendering
 * - Empty results handling
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatInterface } from './ChatInterface';
import { Message, QueryResponse } from '../types';

describe('ChatInterface', () => {
  const mockOnQuerySubmit = vi.fn();

  const createMockMessage = (overrides?: Partial<Message>): Message => ({
    id: '1',
    type: 'user',
    content: 'Test message',
    timestamp: new Date('2024-01-01T12:00:00'),
    ...overrides,
  });

  beforeEach(() => {
    mockOnQuerySubmit.mockClear();
  });

  describe('Message Rendering', () => {
    it('should render user messages with correct styling', () => {
      const userMessage = createMockMessage({
        type: 'user',
        content: 'What are the top products?',
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[userMessage]}
          loading={false}
        />
      );

      const messageElement = screen.getByText('What are the top products?');
      expect(messageElement).toBeInTheDocument();
      
      // User messages should have blue background
      const messageContainer = messageElement.closest('div');
      expect(messageContainer).toHaveClass('bg-blue-600', 'text-white');
    });

    it('should render assistant messages with correct styling', () => {
      const assistantMessage = createMockMessage({
        type: 'assistant',
        content: 'Here are the top products',
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[assistantMessage]}
          loading={false}
        />
      );

      const messageElement = screen.getByText('Here are the top products');
      expect(messageElement).toBeInTheDocument();
      
      // Assistant messages should have white background with border
      const messageContainer = messageElement.closest('div');
      expect(messageContainer).toHaveClass('bg-white', 'border', 'border-gray-200');
    });

    it('should render multiple messages in conversation history', () => {
      const messages: Message[] = [
        createMockMessage({ id: '1', type: 'user', content: 'First question' }),
        createMockMessage({ id: '2', type: 'assistant', content: 'First answer' }),
        createMockMessage({ id: '3', type: 'user', content: 'Second question' }),
      ];

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={messages}
          loading={false}
        />
      );

      expect(screen.getByText('First question')).toBeInTheDocument();
      expect(screen.getByText('First answer')).toBeInTheDocument();
      expect(screen.getByText('Second question')).toBeInTheDocument();
    });

    it('should display welcome message when conversation history is empty', () => {
      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[]}
          loading={false}
        />
      );

      expect(screen.getByText('Welcome to Graph Query System')).toBeInTheDocument();
      expect(screen.getByText(/Ask questions about your business data/i)).toBeInTheDocument();
    });

    it('should render message timestamps', () => {
      const message = createMockMessage({
        timestamp: new Date('2024-01-01T14:30:00'),
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[message]}
          loading={false}
        />
      );

      // Check that timestamp is rendered (format may vary by locale)
      const timestamp = screen.getByText(/2:30|14:30/);
      expect(timestamp).toBeInTheDocument();
    });
  });

  describe('Query Submission', () => {
    it('should submit query when form is submitted', async () => {
      const user = userEvent.setup();
      mockOnQuerySubmit.mockResolvedValue({
        success: true,
        data: [],
      } as QueryResponse);

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[]}
          loading={false}
        />
      );

      const input = screen.getByPlaceholderText(/Ask a question about your data/i);
      const submitButton = screen.getByRole('button', { name: /send/i });

      await user.type(input, 'Show me all orders');
      await user.click(submitButton);

      expect(mockOnQuerySubmit).toHaveBeenCalledWith('Show me all orders');
    });

    it('should clear input after submission', async () => {
      const user = userEvent.setup();
      mockOnQuerySubmit.mockResolvedValue({
        success: true,
        data: [],
      } as QueryResponse);

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[]}
          loading={false}
        />
      );

      const input = screen.getByPlaceholderText(/Ask a question about your data/i) as HTMLInputElement;
      
      await user.type(input, 'Test query');
      await user.click(screen.getByRole('button', { name: /send/i }));

      await waitFor(() => {
        expect(input.value).toBe('');
      });
    });

    it('should not submit empty queries', async () => {
      const user = userEvent.setup();

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[]}
          loading={false}
        />
      );

      const submitButton = screen.getByRole('button', { name: /send/i });
      
      // Button should be disabled when input is empty
      expect(submitButton).toBeDisabled();
      
      await user.click(submitButton);
      expect(mockOnQuerySubmit).not.toHaveBeenCalled();
    });

    it('should not submit whitespace-only queries', async () => {
      const user = userEvent.setup();

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[]}
          loading={false}
        />
      );

      const input = screen.getByPlaceholderText(/Ask a question about your data/i);
      const submitButton = screen.getByRole('button', { name: /send/i });

      await user.type(input, '   ');
      
      // Button should still be disabled for whitespace
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Loading States', () => {
    it('should display loading indicator when loading is true', () => {
      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[]}
          loading={true}
        />
      );

      expect(screen.getByText(/Processing query/i)).toBeInTheDocument();
      
      // Check for spinner element
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('should disable input and button when loading', () => {
      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[]}
          loading={true}
        />
      );

      const input = screen.getByPlaceholderText(/Ask a question about your data/i);
      const submitButton = screen.getByRole('button', { name: /send/i });

      expect(input).toBeDisabled();
      expect(submitButton).toBeDisabled();
    });

    it('should not display loading indicator when loading is false', () => {
      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[]}
          loading={false}
        />
      );

      expect(screen.queryByText(/Processing query/i)).not.toBeInTheDocument();
    });

    it('should prevent submission while loading', async () => {
      const user = userEvent.setup();

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[]}
          loading={true}
        />
      );

      const input = screen.getByPlaceholderText(/Ask a question about your data/i);
      const submitButton = screen.getByRole('button', { name: /send/i });

      await user.type(input, 'Test query');
      await user.click(submitButton);

      expect(mockOnQuerySubmit).not.toHaveBeenCalled();
    });
  });

  describe('Error Message Display', () => {
    it('should display error messages in assistant messages', () => {
      const errorMessage = createMockMessage({
        type: 'assistant',
        content: 'Query failed',
        error: 'Database connection error',
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[errorMessage]}
          loading={false}
        />
      );

      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText('Database connection error')).toBeInTheDocument();
      
      // Error should have red styling
      const errorContainer = screen.getByText('Database connection error').closest('div');
      expect(errorContainer).toHaveClass('bg-red-50', 'border-red-200');
    });

    it('should display error without data results', () => {
      const errorMessage = createMockMessage({
        type: 'assistant',
        content: 'Failed to process query',
        error: 'Invalid Cypher syntax',
        data: undefined,
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[errorMessage]}
          loading={false}
        />
      );

      expect(screen.getByText('Invalid Cypher syntax')).toBeInTheDocument();
      expect(screen.queryByRole('table')).not.toBeInTheDocument();
    });
  });

  describe('Cypher Query Expansion', () => {
    it('should display Cypher query toggle button when cypher is present', () => {
      const messageWithCypher = createMockMessage({
        type: 'assistant',
        content: 'Query results',
        cypher: 'MATCH (n:Order) RETURN n LIMIT 10',
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[messageWithCypher]}
          loading={false}
        />
      );

      expect(screen.getByText('Generated Cypher Query')).toBeInTheDocument();
    });

    it('should toggle Cypher query visibility when button is clicked', async () => {
      const user = userEvent.setup();
      const messageWithCypher = createMockMessage({
        type: 'assistant',
        content: 'Query results',
        cypher: 'MATCH (n:Order) RETURN n LIMIT 10',
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[messageWithCypher]}
          loading={false}
        />
      );

      const toggleButton = screen.getByText('Generated Cypher Query');
      
      // Initially, Cypher should not be visible
      expect(screen.queryByText('MATCH (n:Order) RETURN n LIMIT 10')).not.toBeInTheDocument();

      // Click to expand
      await user.click(toggleButton);
      expect(screen.getByText('MATCH (n:Order) RETURN n LIMIT 10')).toBeInTheDocument();

      // Click to collapse
      await user.click(toggleButton);
      expect(screen.queryByText('MATCH (n:Order) RETURN n LIMIT 10')).not.toBeInTheDocument();
    });

    it('should not display Cypher toggle for user messages', () => {
      const userMessage = createMockMessage({
        type: 'user',
        content: 'Show me orders',
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[userMessage]}
          loading={false}
        />
      );

      expect(screen.queryByText('Generated Cypher Query')).not.toBeInTheDocument();
    });

    it('should not display Cypher toggle when cypher is not present', () => {
      const messageWithoutCypher = createMockMessage({
        type: 'assistant',
        content: 'Query results',
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[messageWithoutCypher]}
          loading={false}
        />
      );

      expect(screen.queryByText('Generated Cypher Query')).not.toBeInTheDocument();
    });
  });

  describe('Query Results Display', () => {
    it('should render query results as a table', () => {
      const messageWithData = createMockMessage({
        type: 'assistant',
        content: 'Here are the results',
        data: [
          { product_id: 'P1', name: 'Product A', price: 100 },
          { product_id: 'P2', name: 'Product B', price: 200 },
        ],
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[messageWithData]}
          loading={false}
        />
      );

      // Check table headers
      expect(screen.getByText('product_id')).toBeInTheDocument();
      expect(screen.getByText('name')).toBeInTheDocument();
      expect(screen.getByText('price')).toBeInTheDocument();

      // Check table data
      expect(screen.getByText('P1')).toBeInTheDocument();
      expect(screen.getByText('Product A')).toBeInTheDocument();
      expect(screen.getByText('100')).toBeInTheDocument();
      expect(screen.getByText('P2')).toBeInTheDocument();
      expect(screen.getByText('Product B')).toBeInTheDocument();
      expect(screen.getByText('200')).toBeInTheDocument();
    });

    it('should display result count', () => {
      const messageWithData = createMockMessage({
        type: 'assistant',
        content: 'Results',
        data: [
          { id: '1', value: 'A' },
          { id: '2', value: 'B' },
          { id: '3', value: 'C' },
        ],
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[messageWithData]}
          loading={false}
        />
      );

      expect(screen.getByText('3 results')).toBeInTheDocument();
    });

    it('should display singular "result" for single row', () => {
      const messageWithData = createMockMessage({
        type: 'assistant',
        content: 'Results',
        data: [{ id: '1', value: 'A' }],
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[messageWithData]}
          loading={false}
        />
      );

      expect(screen.getByText('1 result')).toBeInTheDocument();
    });

    it('should display empty results message when data array is empty', () => {
      const messageWithEmptyData = createMockMessage({
        type: 'assistant',
        content: 'No results found',
        data: [],
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[messageWithEmptyData]}
          loading={false}
        />
      );

      expect(screen.getByText(/No results found for this query/i)).toBeInTheDocument();
      
      // Should have yellow warning styling
      const emptyMessage = screen.getByText(/No results found for this query/i).closest('div');
      expect(emptyMessage).toHaveClass('bg-yellow-50', 'border-yellow-200');
    });

    it('should not display empty results message when error is present', () => {
      const messageWithError = createMockMessage({
        type: 'assistant',
        content: 'Query failed',
        data: [],
        error: 'Some error',
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[messageWithError]}
          loading={false}
        />
      );

      expect(screen.queryByText(/No results found for this query/i)).not.toBeInTheDocument();
      expect(screen.getByText('Some error')).toBeInTheDocument();
    });

    it('should format numeric values with locale formatting', () => {
      const messageWithData = createMockMessage({
        type: 'assistant',
        content: 'Results',
        data: [{ amount: 1234567.89 }],
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[messageWithData]}
          loading={false}
        />
      );

      // Check that number is formatted (may vary by locale, but should have separators)
      const formattedNumber = screen.getByText(/1,234,567.89|1\.234\.567,89/);
      expect(formattedNumber).toBeInTheDocument();
    });

    it('should display "-" for null or undefined values', () => {
      const messageWithData = createMockMessage({
        type: 'assistant',
        content: 'Results',
        data: [{ id: '1', value: null, other: undefined }],
      });

      render(
        <ChatInterface
          onQuerySubmit={mockOnQuerySubmit}
          conversationHistory={[messageWithData]}
          loading={false}
        />
      );

      // Should have two "-" for null and undefined
      const dashes = screen.getAllByText('-');
      expect(dashes.length).toBeGreaterThanOrEqual(2);
    });
  });
});
