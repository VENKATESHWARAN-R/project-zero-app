/**
 * Cart Management Flow Integration Tests
 * Tests for complete cart management workflow
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider } from '@/providers/AuthProvider';
import { CartItem } from '@/components/cart/CartItem';
import { CartSummary } from '@/components/cart/CartSummary';
import { ProductCard } from '@/components/product/ProductCard';
import { Header } from '@/components/layout/Header';
import { CartService } from '@/services/cart';
import { AuthService } from '@/services/auth';

// Mock the services
jest.mock('@/services/cart');
jest.mock('@/services/auth');

const mockCartService = CartService as jest.MockedClass<typeof CartService>;
const mockAuthService = AuthService as jest.MockedClass<typeof AuthService>;

const mockProduct = {
  id: 'product-1',
  name: 'Gaming Laptop Pro',
  description: 'High-performance gaming laptop',
  price: 149999,
  currency: 'USD',
  category: 'electronics',
  imageUrl: 'https://example.com/laptop.jpg',
  inStock: true,
  stockQuantity: 15,
  createdAt: '2025-09-24T10:00:00Z',
  updatedAt: '2025-09-24T10:00:00Z',
};

const mockCartItem = {
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
};

const mockCart = {
  id: 'cart-1',
  user_id: 'user-1',
  items: [mockCartItem],
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

const mockAuthenticatedUser = {
  id: 'user-1',
  email: 'user@example.com',
  firstName: 'John',
  lastName: 'Doe',
  createdAt: '2025-09-24T10:00:00Z',
  updatedAt: '2025-09-24T10:00:00Z',
};

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => '/cart',
  useSearchParams: () => new URLSearchParams(),
}));

const TestWrapper = ({ children, isAuthenticated = true }: { children: React.ReactNode; isAuthenticated?: boolean }) => {
  // Mock auth state
  jest.doMock('@/store/auth', () => ({
    useAuthStore: () => ({
      user: isAuthenticated ? mockAuthenticatedUser : null,
      isAuthenticated,
      tokens: isAuthenticated ? { accessToken: 'mock_token' } : null,
    }),
  }));

  return <AuthProvider>{children}</AuthProvider>;
};

describe('Cart Management Flow Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Add to Cart Flow', () => {
    it('should add product to cart from product card', async () => {
      const user = userEvent.setup();

      // Mock add to cart API
      const mockAddItem = jest.fn().mockResolvedValue({
        id: 'cart-item-1',
        product_id: 'product-1',
        quantity: 1,
        added_at: '2025-09-24T10:00:00Z',
        product: mockCartItem.product,
        cart_summary: {
          total_amount: 149999,
          item_count: 1,
        },
      });
      mockCartService.prototype.addItem = mockAddItem;

      const mockOnAddToCart = jest.fn().mockImplementation(async (productId) => {
        await mockAddItem({ product_id: productId, quantity: 1 });
      });

      render(
        <TestWrapper>
          <ProductCard
            product={mockProduct}
            onAddToCart={mockOnAddToCart}
            onViewDetails={jest.fn()}
          />
        </TestWrapper>
      );

      // Click add to cart
      await user.click(screen.getByText('Add to Cart'));

      // Wait for API call
      await waitFor(() => {
        expect(mockOnAddToCart).toHaveBeenCalledWith('product-1');
      });

      // Should show success feedback
      await waitFor(() => {
        expect(screen.getByText(/added to cart/i)).toBeInTheDocument();
      });
    });

    it('should handle add to cart for unauthenticated user', async () => {
      const user = userEvent.setup();
      const mockNavigate = jest.fn();

      // Mock navigation
      jest.doMock('next/navigation', () => ({
        useRouter: () => ({ push: mockNavigate }),
      }));

      const mockOnAddToCart = jest.fn().mockImplementation(() => {
        // Redirect to login for unauthenticated users
        mockNavigate('/login');
      });

      render(
        <TestWrapper isAuthenticated={false}>
          <ProductCard
            product={mockProduct}
            onAddToCart={mockOnAddToCart}
            onViewDetails={jest.fn()}
          />
        </TestWrapper>
      );

      // Click add to cart
      await user.click(screen.getByText('Add to Cart'));

      // Should redirect to login
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });

    it('should handle out of stock products', async () => {
      const user = userEvent.setup();
      const outOfStockProduct = { ...mockProduct, inStock: false, stockQuantity: 0 };

      render(
        <TestWrapper>
          <ProductCard
            product={outOfStockProduct}
            onAddToCart={jest.fn()}
            onViewDetails={jest.fn()}
          />
        </TestWrapper>
      );

      // Add to cart button should be disabled and show "Out of Stock"
      const addToCartButton = screen.getByText('Out of Stock');
      expect(addToCartButton).toBeDisabled();
    });
  });

  describe('Cart Page Management', () => {
    it('should display cart items correctly', async () => {
      // Mock cart API
      const mockGetCart = jest.fn().mockResolvedValue(mockCart);
      mockCartService.prototype.getCart = mockGetCart;

      render(
        <TestWrapper>
          <div>
            {mockCart.items.map((item) => (
              <CartItem key={item.id} item={item} onUpdateQuantity={jest.fn()} onRemove={jest.fn()} />
            ))}
            <CartSummary cart={mockCart} />
          </div>
        </TestWrapper>
      );

      // Wait for cart to load
      await waitFor(() => {
        expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
        expect(screen.getByText('$2,999.98')).toBeInTheDocument(); // Total for 2 items
      });

      // Check cart summary
      expect(screen.getByText(/2 items/i)).toBeInTheDocument();
      expect(screen.getByText('Total: $2,999.98')).toBeInTheDocument();
    });

    it('should handle empty cart', async () => {
      // Mock empty cart API
      const mockGetCart = jest.fn().mockResolvedValue(mockEmptyCart);
      mockCartService.prototype.getCart = mockGetCart;

      render(
        <TestWrapper>
          <div>
            {mockCart.items.map((item) => (
              <CartItem key={item.id} item={item} onUpdateQuantity={jest.fn()} onRemove={jest.fn()} />
            ))}
            <CartSummary cart={mockCart} />
          </div>
        </TestWrapper>
      );

      // Wait for empty cart message
      await waitFor(() => {
        expect(screen.getByText(/your cart is empty/i)).toBeInTheDocument();
      });

      // Should show continue shopping button
      expect(screen.getByText(/continue shopping/i)).toBeInTheDocument();
    });

    it('should update item quantity', async () => {
      const user = userEvent.setup();

      // Mock initial cart load
      const mockGetCart = jest.fn().mockResolvedValue(mockCart);
      mockCartService.prototype.getCart = mockGetCart;

      // Mock update item
      const mockUpdateItem = jest.fn().mockResolvedValue({
        id: 'cart-item-1',
        quantity: 3,
        cart_summary: { total_amount: 449997, item_count: 3 },
      });
      mockCartService.prototype.updateItem = mockUpdateItem;

      render(
        <TestWrapper>
          <div>
            {mockCart.items.map((item) => (
              <CartItem key={item.id} item={item} onUpdateQuantity={jest.fn()} onRemove={jest.fn()} />
            ))}
            <CartSummary cart={mockCart} />
          </div>
        </TestWrapper>
      );

      // Wait for cart to load
      await waitFor(() => {
        expect(screen.getByDisplayValue('2')).toBeInTheDocument();
      });

      // Mock updated cart after quantity change
      const updatedCart = {
        ...mockCart,
        items: [{ ...mockCartItem, quantity: 3 }],
        total_amount: 449997,
        item_count: 3,
      };
      mockGetCart.mockResolvedValueOnce(updatedCart);

      // Increase quantity
      await user.click(screen.getByLabelText('Increase quantity'));

      // Wait for API call
      await waitFor(() => {
        expect(mockUpdateItem).toHaveBeenCalledWith('cart-item-1', { quantity: 3 });
      });

      // Check updated total
      await waitFor(() => {
        expect(screen.getByText('$4,499.97')).toBeInTheDocument();
      });
    });

    it('should remove item from cart', async () => {
      const user = userEvent.setup();

      // Mock initial cart load
      const mockGetCart = jest.fn().mockResolvedValue(mockCart);
      mockCartService.prototype.getCart = mockGetCart;

      // Mock remove item
      const mockRemoveItem = jest.fn().mockResolvedValue({
        message: 'Item removed from cart',
        removed_item_id: 'cart-item-1',
        cart_summary: { total_amount: 0, item_count: 0 },
      });
      mockCartService.prototype.removeItem = mockRemoveItem;

      render(
        <TestWrapper>
          <div>
            {mockCart.items.map((item) => (
              <CartItem key={item.id} item={item} onUpdateQuantity={jest.fn()} onRemove={jest.fn()} />
            ))}
            <CartSummary cart={mockCart} />
          </div>
        </TestWrapper>
      );

      // Wait for cart to load
      await waitFor(() => {
        expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
      });

      // Mock empty cart after removal
      mockGetCart.mockResolvedValueOnce(mockEmptyCart);

      // Remove item
      await user.click(screen.getByLabelText('Remove item'));

      // Wait for API call
      await waitFor(() => {
        expect(mockRemoveItem).toHaveBeenCalledWith('cart-item-1');
      });

      // Should show empty cart message
      await waitFor(() => {
        expect(screen.getByText(/your cart is empty/i)).toBeInTheDocument();
      });
    });

    it('should clear entire cart', async () => {
      const user = userEvent.setup();

      // Mock initial cart load
      const mockGetCart = jest.fn().mockResolvedValue(mockCart);
      mockCartService.prototype.getCart = mockGetCart;

      // Mock clear cart
      const mockClearCart = jest.fn().mockResolvedValue({
        message: 'Cart cleared successfully',
        cart_summary: { total_amount: 0, item_count: 0 },
      });
      mockCartService.prototype.clearCart = mockClearCart;

      render(
        <TestWrapper>
          <div>
            {mockCart.items.map((item) => (
              <CartItem key={item.id} item={item} onUpdateQuantity={jest.fn()} onRemove={jest.fn()} />
            ))}
            <CartSummary cart={mockCart} />
          </div>
        </TestWrapper>
      );

      // Wait for cart to load
      await waitFor(() => {
        expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
      });

      // Mock empty cart after clearing
      mockGetCart.mockResolvedValueOnce(mockEmptyCart);

      // Clear cart
      await user.click(screen.getByText(/clear cart/i));

      // Wait for confirmation and confirm
      await waitFor(() => {
        expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
      });

      await user.click(screen.getByText(/yes, clear cart/i));

      // Wait for API call
      await waitFor(() => {
        expect(mockClearCart).toHaveBeenCalled();
      });

      // Should show empty cart message
      await waitFor(() => {
        expect(screen.getByText(/your cart is empty/i)).toBeInTheDocument();
      });
    });
  });

  describe('Cart Icon in Header', () => {
    it('should display cart item count in header', async () => {
      // Mock cart summary for header
      const mockGetCartSummary = jest.fn().mockResolvedValue({
        item_count: 3,
        total_amount: 449997,
        currency: 'USD',
        updated_at: '2025-09-24T10:00:00Z',
      });
      mockCartService.prototype.getCartSummary = mockGetCartSummary;

      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      // Wait for cart count to load
      await waitFor(() => {
        expect(screen.getByText('3')).toBeInTheDocument();
      });

      // Cart icon should be visible
      expect(screen.getByLabelText('Cart')).toBeInTheDocument();
    });

    it('should navigate to cart page when cart icon is clicked', async () => {
      const user = userEvent.setup();
      const mockNavigate = jest.fn();

      // Mock navigation
      jest.doMock('next/navigation', () => ({
        useRouter: () => ({ push: mockNavigate }),
      }));

      // Mock cart summary
      const mockGetCartSummary = jest.fn().mockResolvedValue({
        item_count: 2,
        total_amount: 299998,
        currency: 'USD',
        updated_at: '2025-09-24T10:00:00Z',
      });
      mockCartService.prototype.getCartSummary = mockGetCartSummary;

      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      // Wait for cart to load
      await waitFor(() => {
        expect(screen.getByText('2')).toBeInTheDocument();
      });

      // Click cart icon
      await user.click(screen.getByLabelText('Cart'));

      expect(mockNavigate).toHaveBeenCalledWith('/cart');
    });
  });

  describe('Cart Validation', () => {
    it('should validate cart items before checkout', async () => {
      // Mock cart validation
      const mockValidateCart = jest.fn().mockResolvedValue({
        valid: true,
        items: [
          {
            cart_item_id: 'cart-item-1',
            product_id: 'product-1',
            status: 'valid',
            requested_quantity: 2,
            available_quantity: 15,
            current_price: 149999,
            price_changed: false,
          },
        ],
        total_amount: 299998,
        issues: [],
      });
      mockCartService.prototype.validateCart = mockValidateCart;

      // Mock cart load
      const mockGetCart = jest.fn().mockResolvedValue(mockCart);
      mockCartService.prototype.getCart = mockGetCart;

      render(
        <TestWrapper>
          <div>
            {mockCart.items.map((item) => (
              <CartItem key={item.id} item={item} onUpdateQuantity={jest.fn()} onRemove={jest.fn()} />
            ))}
            <CartSummary cart={mockCart} />
          </div>
        </TestWrapper>
      );

      // Wait for cart to load
      await waitFor(() => {
        expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
      });

      // Proceed to checkout (triggers validation)
      fireEvent.click(screen.getByText(/proceed to checkout/i));

      // Wait for validation
      await waitFor(() => {
        expect(mockValidateCart).toHaveBeenCalled();
      });

      // Should proceed to checkout if valid
      expect(screen.getByText(/checkout/i)).toBeInTheDocument();
    });

    it('should handle cart validation issues', async () => {
      // Mock cart validation with issues
      const mockValidateCart = jest.fn().mockResolvedValue({
        valid: false,
        items: [
          {
            cart_item_id: 'cart-item-1',
            product_id: 'product-1',
            status: 'insufficient_stock',
            requested_quantity: 20,
            available_quantity: 15,
            current_price: 149999,
            price_changed: false,
          },
        ],
        total_amount: 2999980,
        issues: [
          {
            type: 'insufficient_stock',
            cart_item_id: 'cart-item-1',
            message: 'Only 15 items available, requested 20',
          },
        ],
      });
      mockCartService.prototype.validateCart = mockValidateCart;

      // Mock cart load
      const mockGetCart = jest.fn().mockResolvedValue(mockCart);
      mockCartService.prototype.getCart = mockGetCart;

      render(
        <TestWrapper>
          <div>
            {mockCart.items.map((item) => (
              <CartItem key={item.id} item={item} onUpdateQuantity={jest.fn()} onRemove={jest.fn()} />
            ))}
            <CartSummary cart={mockCart} />
          </div>
        </TestWrapper>
      );

      // Wait for cart to load
      await waitFor(() => {
        expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
      });

      // Proceed to checkout (triggers validation)
      fireEvent.click(screen.getByText(/proceed to checkout/i));

      // Wait for validation issues
      await waitFor(() => {
        expect(screen.getByText(/only 15 items available/i)).toBeInTheDocument();
      });

      // Checkout should be disabled
      expect(screen.getByText(/resolve issues/i)).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should handle cart API errors gracefully', async () => {
      // Mock cart API error
      const mockGetCart = jest.fn().mockRejectedValue(new Error('Failed to load cart'));
      mockCartService.prototype.getCart = mockGetCart;

      render(
        <TestWrapper>
          <div>
            {mockCart.items.map((item) => (
              <CartItem key={item.id} item={item} onUpdateQuantity={jest.fn()} onRemove={jest.fn()} />
            ))}
            <CartSummary cart={mockCart} />
          </div>
        </TestWrapper>
      );

      // Wait for error message
      await waitFor(() => {
        expect(screen.getByText(/failed to load cart/i)).toBeInTheDocument();
      });

      // Should show retry button
      expect(screen.getByText(/retry/i)).toBeInTheDocument();
    });

    it('should handle network errors during cart operations', async () => {
      const user = userEvent.setup();

      // Mock initial cart load
      const mockGetCart = jest.fn().mockResolvedValue(mockCart);
      mockCartService.prototype.getCart = mockGetCart;

      // Mock network error on update
      const mockUpdateItem = jest.fn().mockRejectedValue(new Error('Network error'));
      mockCartService.prototype.updateItem = mockUpdateItem;

      render(
        <TestWrapper>
          <div>
            {mockCart.items.map((item) => (
              <CartItem key={item.id} item={item} onUpdateQuantity={jest.fn()} onRemove={jest.fn()} />
            ))}
            <CartSummary cart={mockCart} />
          </div>
        </TestWrapper>
      );

      // Wait for cart to load
      await waitFor(() => {
        expect(screen.getByDisplayValue('2')).toBeInTheDocument();
      });

      // Try to update quantity
      await user.click(screen.getByLabelText('Increase quantity'));

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });

      // Should revert to original state
      expect(screen.getByDisplayValue('2')).toBeInTheDocument();
    });
  });
});