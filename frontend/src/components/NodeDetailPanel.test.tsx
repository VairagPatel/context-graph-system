import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { NodeDetailPanel } from './NodeDetailPanel';
import { Node, Edge } from '../types';

describe('NodeDetailPanel', () => {
  const mockOnClose = vi.fn();

  const mockNode: Node = {
    id: 'order-1',
    type: 'Order',
    data: {
      label: 'Order #12345',
      properties: {
        order_id: '12345',
        customer_id: 'cust-001',
        order_date: '2024-01-15',
        total_amount: 1500.50,
        status: 'confirmed',
      },
    },
    position: { x: 100, y: 100 },
  };

  const mockEdge: Edge = {
    id: 'edge-1',
    source: 'order-1',
    target: 'delivery-1',
    type: 'DELIVERED_BY',
    label: 'Delivered By',
  };

  beforeEach(() => {
    mockOnClose.mockClear();
  });

  it('should render nothing when selectedItem is null', () => {
    const { container } = render(
      <NodeDetailPanel selectedItem={null} onClose={mockOnClose} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('should render node details when a node is selected', () => {
    render(<NodeDetailPanel selectedItem={mockNode} onClose={mockOnClose} />);

    // Check entity type header
    expect(screen.getByText('Order')).toBeInTheDocument();
    expect(screen.getByText('Order #12345')).toBeInTheDocument();

    // Check properties section
    expect(screen.getByText('Properties')).toBeInTheDocument();
    expect(screen.getByText('order_id')).toBeInTheDocument();
    expect(screen.getByText('12345')).toBeInTheDocument();
    expect(screen.getByText('total_amount')).toBeInTheDocument();
    expect(screen.getByText('1,500.5')).toBeInTheDocument();
  });

  it('should render edge details when an edge is selected', () => {
    render(<NodeDetailPanel selectedItem={mockEdge} onClose={mockOnClose} />);

    // Check relationship type header
    expect(screen.getByText('Relationship')).toBeInTheDocument();
    expect(screen.getByText('DELIVERED_BY')).toBeInTheDocument();

    // Check connection info
    expect(screen.getByText('Connection')).toBeInTheDocument();
    expect(screen.getByText('Source')).toBeInTheDocument();
    expect(screen.getByText('order-1')).toBeInTheDocument();
    expect(screen.getByText('Target')).toBeInTheDocument();
    expect(screen.getByText('delivery-1')).toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', () => {
    render(<NodeDetailPanel selectedItem={mockNode} onClose={mockOnClose} />);

    const closeButton = screen.getByLabelText('Close panel');
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should call onClose when overlay backdrop is clicked', () => {
    render(<NodeDetailPanel selectedItem={mockNode} onClose={mockOnClose} />);

    const overlay = screen.getByRole('generic', { hidden: true });
    fireEvent.click(overlay);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should display "No properties available" when node has no properties', () => {
    const nodeWithoutProps: Node = {
      ...mockNode,
      data: {
        label: 'Empty Node',
        properties: {},
      },
    };

    render(<NodeDetailPanel selectedItem={nodeWithoutProps} onClose={mockOnClose} />);

    expect(screen.getByText('No properties available')).toBeInTheDocument();
  });

  it('should format property values correctly', () => {
    const nodeWithVariousTypes: Node = {
      id: 'test-1',
      type: 'Test',
      data: {
        label: 'Test Node',
        properties: {
          string_prop: 'test value',
          number_prop: 1234.56,
          null_prop: null,
          undefined_prop: undefined,
        },
      },
      position: { x: 0, y: 0 },
    };

    render(<NodeDetailPanel selectedItem={nodeWithVariousTypes} onClose={mockOnClose} />);

    expect(screen.getByText('test value')).toBeInTheDocument();
    expect(screen.getByText('1,234.56')).toBeInTheDocument();
    // null and undefined should be formatted as '-'
    const dashes = screen.getAllByText('-');
    expect(dashes.length).toBeGreaterThanOrEqual(2);
  });
});
