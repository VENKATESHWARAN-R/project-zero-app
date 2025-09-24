/**
 * Cart Store Tests
 * Tests for the cart management Zustand store
 */

import { act, renderHook } from '@testing-library/react';
import { useCartStore } from '@/store/cart';
import { CartService } from '@/services/cart';

// Mock the cart service
jest.mock('@/services/cart');

const mockCartService = CartService as jest.MockedClass<typeof CartService>;

const mockCart = {
  id: 'cart-1',
  user_id: 'user-1',
  items: [
    {
      id: 'cart-item-1',
      product_id: 'product-1',
      quantity: 2,
      added_at: '2025-09-24T10:00:00Z',
      product: {
        id: 'product-1',
        name: 'Gaming Laptop Pro',
        price: 149999,
        currency: 'USD',
        image_url: 'https://example.com/laptop.jpg',
        in_stock: true,
        stock_quantity: 15,
      },
    },
  ],
  total_amount: 299998,
  item_count: 2,
  currency: 'USD',
  created_at: '2025-09-24T09:30:00Z',
  updated_at: '2025-09-24T10:00:00Z',
};

const mockEmptyCart = {
  id: 'cart-1',
  user_id: 'user-1',
  items: [],
  total_amount: 0,
  item_count: 0,
  currency: 'USD',
  created_at: '2025-09-24T09:30:00Z',
  updated_at: '2025-09-24T09:30:00Z',
};

describe('Cart Store', () => {
  beforeEach(() => {
    // Reset store state
    useCartStore.setState({
      cart: null,
      isLoading: false,
      error: null,
    });

    // Reset mocks
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useCartStore());

      expect(result.current.cart).toBeNull();
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });

  describe('Load Cart', () => {
    it('should load cart successfully', async () => {
      const mockGetCart = jest.fn().mockResolvedValue(mockCart);
      mockCartService.prototype.getCart = mockGetCart;

      const { result } = renderHook(() => useCartStore());

      await act(async () => {
        await result.current.loadCart();
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.cart).toEqual({
        id: 'cart-1',
        userId: 'user-1',
        items: [
          {
            id: 'cart-item-1',
            productId: 'product-1',
            quantity: 2,
            addedAt: '2025-09-24T10:00:00Z',
            product: {
              id: 'product-1',
              name: 'Gaming Laptop Pro',
              price: 149999,
              currency: 'USD',
              imageUrl: 'https://example.com/laptop.jpg',
              inStock: true,
              stockQuantity: 15,
            },
          },
        ],
        totalAmount: 299998,
        itemCount: 2,
        currency: 'USD',
        createdAt: '2025-09-24T09:30:00Z',
        updatedAt: '2025-09-24T10:00:00Z',
      });
      expect(result.current.error).toBeNull();
    });

    it('should handle load cart failure', async () => {
      const mockGetCart = jest.fn().mockRejectedValue(new Error('Failed to load cart'));
      mockCartService.prototype.getCart = mockGetCart;

      const { result } = renderHook(() => useCartStore());

      await act(async () => {
        await result.current.loadCart();
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.cart).toBeNull();
      expect(result.current.error).toBe('Failed to load cart');
    });

    it('should set loading state during cart load', async () => {
      const mockGetCart = jest.fn().mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockCart), 100))
      );
      mockCartService.prototype.getCart = mockGetCart;

      const { result } = renderHook(() => useCartStore());

      act(() => {
        result.current.loadCart();
      });

      expect(result.current.isLoading).toBe(true);

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 150));
      });

      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('Add Item', () => {
    it('should add item to cart successfully', async () => {
      const mockAddItem = jest.fn().mockResolvedValue({
        id: 'cart-item-1',
        product_id: 'product-1',
        quantity: 1,
        added_at: '2025-09-24T10:00:00Z',
        product: {
          id: 'product-1',
          name: 'Gaming Laptop Pro',
          price: 149999,
          currency: 'USD',
        },
        cart_summary: {
          total_amount: 149999,
          item_count: 1,
        },
      });
      mockCartService.prototype.addItem = mockAddItem;

      const { result } = renderHook(() => useCartStore());

      await act(async () => {
        await result.current.addItem('product-1', 1);
      });

      expect(mockAddItem).toHaveBeenCalledWith({
        product_id: 'product-1',
        quantity: 1,
      });
      expect(result.current.error).toBeNull();
    });

    it('should handle add item failure', async () => {
      const mockAddItem = jest.fn().mockRejectedValue(new Error('Product not found'));
      mockCartService.prototype.addItem = mockAddItem;

      const { result } = renderHook(() => useCartStore());

      await act(async () => {
        await result.current.addItem('invalid-product', 1);
      });

      expect(result.current.error).toBe('Product not found');
    });

    it('should reload cart after successful add', async () => {
      const mockAddItem = jest.fn().mockResolvedValue({
        id: 'cart-item-1',
        product_id: 'product-1',
        quantity: 1,
        cart_summary: { total_amount: 149999, item_count: 1 },
      });
      const mockGetCart = jest.fn().mockResolvedValue(mockCart);
      mockCartService.prototype.addItem = mockAddItem;
      mockCartService.prototype.getCart = mockGetCart;

      const { result } = renderHook(() => useCartStore());

      await act(async () => {
        await result.current.addItem('product-1', 1);
      });

      expect(mockGetCart).toHaveBeenCalled();
    });
  });

  describe('Update Item Quantity', () => {
    it('should update item quantity successfully', async () => {
      const mockUpdateItem = jest.fn().mockResolvedValue({
        id: 'cart-item-1',
        quantity: 3,
        cart_summary: { total_amount: 449997, item_count: 3 },
      });
      const mockGetCart = jest.fn().mockResolvedValue(mockCart);
      mockCartService.prototype.updateItem = mockUpdateItem;
      mockCartService.prototype.getCart = mockGetCart;

      const { result } = renderHook(() => useCartStore());

      await act(async () => {
        await result.current.updateItemQuantity('cart-item-1', 3);
      });

      expect(mockUpdateItem).toHaveBeenCalledWith('cart-item-1', { quantity: 3 });
      expect(mockGetCart).toHaveBeenCalled();
    });

    it('should handle update failure', async () => {
      const mockUpdateItem = jest.fn().mockRejectedValue(new Error('Item not found'));
      mockCartService.prototype.updateItem = mockUpdateItem;

      const { result } = renderHook(() => useCartStore());

      await act(async () => {
        await result.current.updateItemQuantity('invalid-item', 3);
      });

      expect(result.current.error).toBe('Item not found');
    });
  });

  describe('Remove Item', () => {
    it('should remove item successfully', async () => {
      const mockRemoveItem = jest.fn().mockResolvedValue({
        message: 'Item removed from cart',
        removed_item_id: 'cart-item-1',
        cart_summary: { total_amount: 0, item_count: 0 },
      });
      const mockGetCart = jest.fn().mockResolvedValue(mockEmptyCart);
      mockCartService.prototype.removeItem = mockRemoveItem;
      mockCartService.prototype.getCart = mockGetCart;

      const { result } = renderHook(() => useCartStore());

      await act(async () => {
        await result.current.removeItem('cart-item-1');
      });

      expect(mockRemoveItem).toHaveBeenCalledWith('cart-item-1');
      expect(mockGetCart).toHaveBeenCalled();
    });
  });

  describe('Clear Cart', () => {
    it('should clear cart successfully', async () => {
      const mockClearCart = jest.fn().mockResolvedValue({
        message: 'Cart cleared successfully',
        cart_summary: { total_amount: 0, item_count: 0 },
      });
      const mockGetCart = jest.fn().mockResolvedValue(mockEmptyCart);
      mockCartService.prototype.clearCart = mockClearCart;
      mockCartService.prototype.getCart = mockGetCart;

      const { result } = renderHook(() => useCartStore());

      await act(async () => {
        await result.current.clearCart();
      });

      expect(mockClearCart).toHaveBeenCalled();
      expect(mockGetCart).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should clear error', () => {
      const { result } = renderHook(() => useCartStore());

      act(() => {
        useCartStore.setState({ error: 'Some error' });
      });

      expect(result.current.error).toBe('Some error');

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('Computed Properties', () => {
    it('should calculate total items correctly', () => {
      const { result } = renderHook(() => useCartStore());

      act(() => {
        useCartStore.setState({
          cart: {
            id: 'cart-1',
            userId: 'user-1',
            items: [
              { id: '1', productId: 'p1', quantity: 2, addedAt: '', product: {} as any },
              { id: '2', productId: 'p2', quantity: 3, addedAt: '', product: {} as any },
            ],
            totalAmount: 0,
            itemCount: 5,
            currency: 'USD',
            createdAt: '',
            updatedAt: '',
          },
        });
      });

      expect(result.current.totalItems).toBe(5);
    });

    it('should return 0 total items for null cart', () => {
      const { result } = renderHook(() => useCartStore());

      expect(result.current.totalItems).toBe(0);
    });

    it('should check if cart is empty', () => {
      const { result } = renderHook(() => useCartStore());

      expect(result.current.isEmpty).toBe(true);

      act(() => {
        useCartStore.setState({ cart: mockCart });
      });

      expect(result.current.isEmpty).toBe(false);
    });
  });
});