import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import GraphVisualizer from './GraphVisualizer';
import { Node, Edge } from '../types';

/**
 * Component tests for GraphVisualizer
 * 
 * **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 13.2, 13.3, 13.4**
 * 
 * Tests cover:
 * - Node rendering with correct colors per entity type
 * - Edge rendering with relationship labels
 * - Node click interactions and callbacks
 * - Highlighted node styling with borders and shadows
 */
describe('GraphVisualizer', () => {
  const mockOnNodeClick = vi.fn();
  const mockOnEdgeClick = vi.fn();

  beforeEach(() => {
    mockOnNodeClick.mockClear();
    mockOnEdgeClick.mockClear();
  });

  const mockNodes: Node[] = [
    {
      id: '1',
      type: 'Order',
      data: {
        label: 'Order #1',
        properties: { order_id: '1', total_amount: 100 },
      },
      position: { x: 0, y: 0 },
    },
    {
      id: '2',
      type: 'Delivery',
      data: {
        label: 'Delivery #1',
        properties: { delivery_id: '1', status: 'delivered' },
      },
      position: { x: 200, y: 0 },
    },
    {
      id: '3',
      type: 'Invoice',
      data: {
        label: 'Invoice #1',
        properties: { invoice_id: '1', amount: 100 },
      },
      position: { x: 400, y: 0 },
    },
  ];

  const mockEdges: Edge[] = [
    {
      id: 'e1-2',
      source: '1',
      target: '2',
      type: 'DELIVERED_BY',
      label: 'DELIVERED_BY',
    },
    {
      id: 'e1-3',
      source: '1',
      target: '3',
      type: 'BILLED_BY',
      label: 'BILLED_BY',
    },
  ];

  describe('Basic Rendering', () => {
    it('renders without crashing', () => {
      render(
        <GraphVisualizer
          nodes={mockNodes}
          edges={mockEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      expect(document.querySelector('.react-flow')).toBeTruthy();
    });

    it('renders nodes with correct labels', () => {
      render(
        <GraphVisualizer
          nodes={mockNodes}
          edges={mockEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      expect(screen.getByText('Order #1')).toBeTruthy();
      expect(screen.getByText('Delivery #1')).toBeTruthy();
      expect(screen.getByText('Invoice #1')).toBeTruthy();
    });

    it('renders with controls and minimap', () => {
      const { container } = render(
        <GraphVisualizer
          nodes={mockNodes}
          edges={mockEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      expect(container.querySelector('.react-flow__controls')).toBeTruthy();
      expect(container.querySelector('.react-flow__minimap')).toBeTruthy();
    });
  });

  describe('Node Rendering with Colors - Requirement 3.1', () => {
    it('renders Order nodes with blue color', () => {
      const orderNodes: Node[] = [
        {
          id: 'order1',
          type: 'Order',
          data: { label: 'Order #1', properties: {} },
          position: { x: 0, y: 0 },
        },
      ];

      const { container } = render(
        <GraphVisualizer
          nodes={orderNodes}
          edges={[]}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      const node = container.querySelector('[data-id="order1"]');
      expect(node).toBeTruthy();
      const nodeElement = node as HTMLElement;
      const style = nodeElement.style.background || nodeElement.getAttribute('style');
      expect(style).toContain('#3b82f6'); // blue
    });

    it('renders Delivery nodes with green color', () => {
      const deliveryNodes: Node[] = [
        {
          id: 'delivery1',
          type: 'Delivery',
          data: { label: 'Delivery #1', properties: {} },
          position: { x: 0, y: 0 },
        },
      ];

      const { container } = render(
        <GraphVisualizer
          nodes={deliveryNodes}
          edges={[]}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      const node = container.querySelector('[data-id="delivery1"]');
      expect(node).toBeTruthy();
      const nodeElement = node as HTMLElement;
      const style = nodeElement.style.background || nodeElement.getAttribute('style');
      expect(style).toContain('#22c55e'); // green
    });

    it('renders Invoice nodes with orange color', () => {
      const invoiceNodes: Node[] = [
        {
          id: 'invoice1',
          type: 'Invoice',
          data: { label: 'Invoice #1', properties: {} },
          position: { x: 0, y: 0 },
        },
      ];

      const { container } = render(
        <GraphVisualizer
          nodes={invoiceNodes}
          edges={[]}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      const node = container.querySelector('[data-id="invoice1"]');
      expect(node).toBeTruthy();
      const nodeElement = node as HTMLElement;
      const style = nodeElement.style.background || nodeElement.getAttribute('style');
      expect(style).toContain('#f97316'); // orange
    });

    it('renders Payment nodes with purple color', () => {
      const paymentNodes: Node[] = [
        {
          id: 'payment1',
          type: 'Payment',
          data: { label: 'Payment #1', properties: {} },
          position: { x: 0, y: 0 },
        },
      ];

      const { container } = render(
        <GraphVisualizer
          nodes={paymentNodes}
          edges={[]}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      const node = container.querySelector('[data-id="payment1"]');
      expect(node).toBeTruthy();
      const nodeElement = node as HTMLElement;
      const style = nodeElement.style.background || nodeElement.getAttribute('style');
      expect(style).toContain('#a855f7'); // purple
    });

    it('renders Customer nodes with pink color', () => {
      const customerNodes: Node[] = [
        {
          id: 'customer1',
          type: 'Customer',
          data: { label: 'Customer #1', properties: {} },
          position: { x: 0, y: 0 },
        },
      ];

      const { container } = render(
        <GraphVisualizer
          nodes={customerNodes}
          edges={[]}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      const node = container.querySelector('[data-id="customer1"]');
      expect(node).toBeTruthy();
      const nodeElement = node as HTMLElement;
      const style = nodeElement.style.background || nodeElement.getAttribute('style');
      expect(style).toContain('#ec4899'); // pink
    });

    it('renders Product nodes with yellow color', () => {
      const productNodes: Node[] = [
        {
          id: 'product1',
          type: 'Product',
          data: { label: 'Product #1', properties: {} },
          position: { x: 0, y: 0 },
        },
      ];

      const { container } = render(
        <GraphVisualizer
          nodes={productNodes}
          edges={[]}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      const node = container.querySelector('[data-id="product1"]');
      expect(node).toBeTruthy();
      const nodeElement = node as HTMLElement;
      const style = nodeElement.style.background || nodeElement.getAttribute('style');
      expect(style).toContain('#eab308'); // yellow
    });

    it('renders Address nodes with gray color', () => {
      const addressNodes: Node[] = [
        {
          id: 'address1',
          type: 'Address',
          data: { label: 'Address #1', properties: {} },
          position: { x: 0, y: 0 },
        },
      ];

      const { container } = render(
        <GraphVisualizer
          nodes={addressNodes}
          edges={[]}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      const node = container.querySelector('[data-id="address1"]');
      expect(node).toBeTruthy();
      const nodeElement = node as HTMLElement;
      const style = nodeElement.style.background || nodeElement.getAttribute('style');
      expect(style).toContain('#6b7280'); // gray
    });
  });

  describe('Edge Rendering with Labels - Requirement 3.2', () => {
    it('renders edges with relationship type labels', () => {
      render(
        <GraphVisualizer
          nodes={mockNodes}
          edges={mockEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      expect(screen.getByText('DELIVERED_BY')).toBeTruthy();
      expect(screen.getByText('BILLED_BY')).toBeTruthy();
    });

    it('renders multiple edges between different nodes', () => {
      const multiEdges: Edge[] = [
        {
          id: 'e1',
          source: '1',
          target: '2',
          type: 'DELIVERED_BY',
          label: 'DELIVERED_BY',
        },
        {
          id: 'e2',
          source: '1',
          target: '3',
          type: 'BILLED_BY',
          label: 'BILLED_BY',
        },
        {
          id: 'e3',
          source: '3',
          target: '2',
          type: 'PAID_BY',
          label: 'PAID_BY',
        },
      ];

      const { container } = render(
        <GraphVisualizer
          nodes={mockNodes}
          edges={multiEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      const edges = container.querySelectorAll('.react-flow__edge');
      expect(edges.length).toBe(3);
    });
  });

  describe('Node Click Interactions - Requirement 3.3', () => {
    it('calls onNodeClick when a node is clicked', () => {
      const { container } = render(
        <GraphVisualizer
          nodes={mockNodes}
          edges={mockEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      const node = container.querySelector('[data-id="1"]');
      expect(node).toBeTruthy();
      
      fireEvent.click(node as Element);
      
      expect(mockOnNodeClick).toHaveBeenCalledTimes(1);
      expect(mockOnNodeClick).toHaveBeenCalledWith(
        expect.objectContaining({
          id: '1',
          type: 'Order',
        })
      );
    });

    it('passes correct node data to onNodeClick callback', () => {
      const { container } = render(
        <GraphVisualizer
          nodes={mockNodes}
          edges={mockEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      const deliveryNode = container.querySelector('[data-id="2"]');
      fireEvent.click(deliveryNode as Element);

      expect(mockOnNodeClick).toHaveBeenCalledWith(
        expect.objectContaining({
          id: '2',
          type: 'Delivery',
          data: expect.objectContaining({
            label: 'Delivery #1',
            properties: { delivery_id: '1', status: 'delivered' },
          }),
        })
      );
    });

    it('calls onEdgeClick when an edge is clicked', () => {
      const { container } = render(
        <GraphVisualizer
          nodes={mockNodes}
          edges={mockEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
        />
      );

      const edge = container.querySelector('[data-id="e1-2"]');
      expect(edge).toBeTruthy();
      
      fireEvent.click(edge as Element);
      
      expect(mockOnEdgeClick).toHaveBeenCalledTimes(1);
      expect(mockOnEdgeClick).toHaveBeenCalledWith(
        expect.objectContaining({
          id: 'e1-2',
          source: '1',
          target: '2',
          type: 'DELIVERED_BY',
        })
      );
    });
  });

  describe('Highlighted Node Styling - Requirement 3.4, 13.2, 13.3, 13.4', () => {
    it('applies highlighted styling to specified nodes', () => {
      const { container } = render(
        <GraphVisualizer
          nodes={mockNodes}
          edges={mockEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
          highlightedNodeIds={['1']}
        />
      );

      const highlightedNode = container.querySelector('[data-id="1"]') as HTMLElement;
      expect(highlightedNode).toBeTruthy();
      
      const style = highlightedNode.getAttribute('style') || '';
      expect(style).toContain('3px solid #fbbf24'); // thicker border
      expect(style).toContain('box-shadow'); // glow effect
    });

    it('applies normal styling to non-highlighted nodes', () => {
      const { container } = render(
        <GraphVisualizer
          nodes={mockNodes}
          edges={mockEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
          highlightedNodeIds={['1']}
        />
      );

      const normalNode = container.querySelector('[data-id="2"]') as HTMLElement;
      expect(normalNode).toBeTruthy();
      
      const style = normalNode.getAttribute('style') || '';
      expect(style).toContain('2px solid #1f2937'); // normal border
    });

    it('highlights multiple nodes when multiple IDs are provided', () => {
      const { container } = render(
        <GraphVisualizer
          nodes={mockNodes}
          edges={mockEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
          highlightedNodeIds={['1', '3']}
        />
      );

      const node1 = container.querySelector('[data-id="1"]') as HTMLElement;
      const node3 = container.querySelector('[data-id="3"]') as HTMLElement;
      
      expect(node1.getAttribute('style')).toContain('3px solid #fbbf24');
      expect(node3.getAttribute('style')).toContain('3px solid #fbbf24');
    });

    it('renders without highlighted nodes when highlightedNodeIds is empty', () => {
      const { container } = render(
        <GraphVisualizer
          nodes={mockNodes}
          edges={mockEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
          highlightedNodeIds={[]}
        />
      );

      const nodes = container.querySelectorAll('[data-id]');
      nodes.forEach((node) => {
        const style = (node as HTMLElement).getAttribute('style') || '';
        expect(style).toContain('2px solid #1f2937'); // all normal borders
      });
    });

    it('updates highlighted nodes when highlightedNodeIds prop changes', () => {
      const { container, rerender } = render(
        <GraphVisualizer
          nodes={mockNodes}
          edges={mockEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
          highlightedNodeIds={['1']}
        />
      );

      let node1 = container.querySelector('[data-id="1"]') as HTMLElement;
      expect(node1.getAttribute('style')).toContain('3px solid #fbbf24');

      rerender(
        <GraphVisualizer
          nodes={mockNodes}
          edges={mockEdges}
          onNodeClick={mockOnNodeClick}
          onEdgeClick={mockOnEdgeClick}
          highlightedNodeIds={['2']}
        />
      );

      node1 = container.querySelector('[data-id="1"]') as HTMLElement;
      const node2 = container.querySelector('[data-id="2"]') as HTMLElement;
      
      expect(node1.getAttribute('style')).toContain('2px solid #1f2937');
      expect(node2.getAttribute('style')).toContain('3px solid #fbbf24');
    });
  });
});
