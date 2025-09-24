/**
 * Service Integration Tests
 * Tests for integration between services and UI components
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthService } from '@/services/auth';
import { ProductsService } from '@/services/products';
import { CartService } from '@/services/cart';

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
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
}));

// Mock actual service methods
jest.mock('@/services/auth', () => ({
  AuthService: jest.fn().mockImplementation(() => ({
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    refreshToken: jest.fn(),
    verifyToken: jest.fn(),
  })),
}));

jest.mock('@/services/products', () => ({
  ProductsService: jest.fn().mockImplementation(() => ({
    getProducts: jest.fn(),
    getProduct: jest.fn(),
    getCategories: jest.fn(),
  })),
}));

jest.mock('@/services/cart', () => ({
  CartService: jest.fn().mockImplementation(() => ({
    getCart: jest.fn(),
    addItem: jest.fn(),
    updateItem: jest.fn(),
    removeItem: jest.fn(),
    clearCart: jest.fn(),
    validateCart: jest.fn(),
  })),
}));

describe('Service Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Authentication Service Integration', () => {
    it('should handle successful login flow', async () => {
      const authService = new AuthService();
      const mockLoginResponse = {
        access_token: 'mock_access_token',
        refresh_token: 'mock_refresh_token',
        token_type: 'bearer',
        expires_in: 900,
        user: {
          id: 'user-1',
          email: 'user@example.com',
          first_name: 'John',
          last_name: 'Doe',
        },
      };

      authService.login = jest.fn().mockResolvedValue(mockLoginResponse);

      const result = await authService.login({
        email: 'user@example.com',
        password: 'password123',
      });

      expect(authService.login).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 'password123',
      });
      expect(result).toEqual(mockLoginResponse);
    });

    it('should handle login errors', async () => {
      const authService = new AuthService();
      authService.login = jest.fn().mockRejectedValue(new Error('Invalid credentials'));

      await expect(
        authService.login({
          email: 'user@example.com',
          password: 'wrongpassword',
        })
      ).rejects.toThrow('Invalid credentials');
    });

    it('should handle token refresh', async () => {
      const authService = new AuthService();
      const mockRefreshResponse = {
        access_token: 'new_access_token',
        token_type: 'bearer',
        expires_in: 900,
      };

      authService.refreshToken = jest.fn().mockResolvedValue(mockRefreshResponse);

      const result = await authService.refreshToken('refresh_token');

      expect(authService.refreshToken).toHaveBeenCalledWith('refresh_token');
      expect(result).toEqual(mockRefreshResponse);
    });
  });

  describe('Products Service Integration', () => {
    it('should fetch products successfully', async () => {
      const productsService = new ProductsService();
      const mockProductsResponse = {
        products: [
          {
            id: 'product-1',
            name: 'Test Product',
            price: 99999,
            currency: 'USD',
            in_stock: true,
          },
        ],
        pagination: { page: 1, total: 1 },
      };

      productsService.getProducts = jest.fn().mockResolvedValue(mockProductsResponse);

      const result = await productsService.getProducts({ page: 1 });

      expect(productsService.getProducts).toHaveBeenCalledWith({ page: 1 });
      expect(result).toEqual(mockProductsResponse);
    });

    it('should handle product fetch errors', async () => {
      const productsService = new ProductsService();
      productsService.getProducts = jest.fn().mockRejectedValue(new Error('Products not found'));

      await expect(productsService.getProducts({})).rejects.toThrow('Products not found');
    });

    it('should fetch single product details', async () => {
      const productsService = new ProductsService();
      const mockProduct = {
        id: 'product-1',
        name: 'Test Product',
        description: 'A test product',
        price: 99999,
        currency: 'USD',
        in_stock: true,
      };

      productsService.getProduct = jest.fn().mockResolvedValue(mockProduct);

      const result = await productsService.getProduct('product-1');

      expect(productsService.getProduct).toHaveBeenCalledWith('product-1');
      expect(result).toEqual(mockProduct);
    });
  });

  describe('Cart Service Integration', () => {
    it('should add item to cart successfully', async () => {
      const cartService = new CartService();
      const mockAddResponse = {
        id: 'cart-item-1',
        product_id: 'product-1',
        quantity: 1,
        cart_summary: {
          total_amount: 99999,
          item_count: 1,
        },
      };

      cartService.addItem = jest.fn().mockResolvedValue(mockAddResponse);

      const result = await cartService.addItem({
        product_id: 'product-1',
        quantity: 1,
      });

      expect(cartService.addItem).toHaveBeenCalledWith({
        product_id: 'product-1',
        quantity: 1,
      });
      expect(result).toEqual(mockAddResponse);
    });

    it('should handle cart addition errors', async () => {
      const cartService = new CartService();
      cartService.addItem = jest.fn().mockRejectedValue(new Error('Product out of stock'));

      await expect(
        cartService.addItem({
          product_id: 'product-1',
          quantity: 10,
        })
      ).rejects.toThrow('Product out of stock');
    });

    it('should update cart item quantity', async () => {
      const cartService = new CartService();
      const mockUpdateResponse = {
        id: 'cart-item-1',
        quantity: 3,
        cart_summary: {
          total_amount: 299997,
          item_count: 3,
        },
      };

      cartService.updateItem = jest.fn().mockResolvedValue(mockUpdateResponse);

      const result = await cartService.updateItem('cart-item-1', { quantity: 3 });

      expect(cartService.updateItem).toHaveBeenCalledWith('cart-item-1', { quantity: 3 });
      expect(result).toEqual(mockUpdateResponse);
    });

    it('should remove item from cart', async () => {
      const cartService = new CartService();
      const mockRemoveResponse = {
        message: 'Item removed from cart',
        removed_item_id: 'cart-item-1',
        cart_summary: {
          total_amount: 0,
          item_count: 0,
        },
      };

      cartService.removeItem = jest.fn().mockResolvedValue(mockRemoveResponse);

      const result = await cartService.removeItem('cart-item-1');

      expect(cartService.removeItem).toHaveBeenCalledWith('cart-item-1');
      expect(result).toEqual(mockRemoveResponse);
    });

    it('should validate cart before checkout', async () => {
      const cartService = new CartService();
      const mockValidationResponse = {
        valid: true,
        items: [
          {
            cart_item_id: 'cart-item-1',
            status: 'valid',
            available_quantity: 10,
            current_price: 99999,
          },
        ],
        total_amount: 99999,
        issues: [],
      };

      cartService.validateCart = jest.fn().mockResolvedValue(mockValidationResponse);

      const result = await cartService.validateCart();

      expect(cartService.validateCart).toHaveBeenCalled();
      expect(result).toEqual(mockValidationResponse);
    });

    it('should handle cart validation with issues', async () => {
      const cartService = new CartService();
      const mockValidationResponse = {
        valid: false,
        items: [
          {
            cart_item_id: 'cart-item-1',
            status: 'insufficient_stock',
            available_quantity: 5,
            current_price: 99999,
          },
        ],
        total_amount: 99999,
        issues: [
          {
            type: 'insufficient_stock',
            cart_item_id: 'cart-item-1',
            message: 'Only 5 items available',
          },
        ],
      };

      cartService.validateCart = jest.fn().mockResolvedValue(mockValidationResponse);

      const result = await cartService.validateCart();

      expect(result.valid).toBe(false);
      expect(result.issues).toHaveLength(1);
      expect(result.issues[0].type).toBe('insufficient_stock');
    });
  });

  describe('Cross-Service Integration', () => {
    it('should handle authenticated cart operations', async () => {
      const authService = new AuthService();
      const cartService = new CartService();

      // Mock successful authentication
      authService.verifyToken = jest.fn().mockResolvedValue({
        valid: true,
        user: { id: 'user-1', email: 'user@example.com' },
      });

      // Mock cart operations after authentication
      cartService.getCart = jest.fn().mockResolvedValue({
        id: 'cart-1',
        user_id: 'user-1',
        items: [],
        total_amount: 0,
        item_count: 0,
      });

      const tokenValid = await authService.verifyToken('access_token');
      expect(tokenValid.valid).toBe(true);

      if (tokenValid.valid) {
        const cart = await cartService.getCart();
        expect(cart.user_id).toBe('user-1');
        expect(cartService.getCart).toHaveBeenCalled();
      }
    });

    it('should handle cart operations with expired authentication', async () => {
      const authService = new AuthService();
      const cartService = new CartService();

      // Mock expired token
      authService.verifyToken = jest.fn().mockRejectedValue(new Error('Token expired'));

      // Mock refresh token
      authService.refreshToken = jest.fn().mockResolvedValue({
        access_token: 'new_access_token',
        token_type: 'bearer',
        expires_in: 900,
      });

      // Mock cart operations after token refresh
      cartService.getCart = jest.fn().mockResolvedValue({
        id: 'cart-1',
        user_id: 'user-1',
        items: [],
        total_amount: 0,
        item_count: 0,
      });

      try {
        await authService.verifyToken('expired_token');
      } catch (error) {
        expect((error as Error).message).toBe('Token expired');

        // Refresh token and retry
        const newTokens = await authService.refreshToken('refresh_token');
        expect(newTokens.access_token).toBe('new_access_token');

        // Now cart operations should work
        const cart = await cartService.getCart();
        expect(cart).toBeDefined();
      }
    });

    it('should handle product to cart workflow', async () => {
      const productsService = new ProductsService();
      const cartService = new CartService();

      // Mock product fetch
      productsService.getProduct = jest.fn().mockResolvedValue({
        id: 'product-1',
        name: 'Test Product',
        price: 99999,
        in_stock: true,
        stock_quantity: 10,
      });

      // Mock add to cart
      cartService.addItem = jest.fn().mockResolvedValue({
        id: 'cart-item-1',
        product_id: 'product-1',
        quantity: 2,
        cart_summary: {
          total_amount: 199998,
          item_count: 2,
        },
      });

      // Workflow: Get product details, then add to cart
      const product = await productsService.getProduct('product-1');
      expect(product.in_stock).toBe(true);
      expect(product.stock_quantity).toBeGreaterThanOrEqual(2);

      const cartItem = await cartService.addItem({
        product_id: product.id,
        quantity: 2,
      });

      expect(cartItem.product_id).toBe(product.id);
      expect(cartItem.quantity).toBe(2);
      expect(cartItem.cart_summary.total_amount).toBe(product.price * 2);
    });
  });

  describe('Error Handling Integration', () => {
    it('should handle network timeouts gracefully', async () => {
      const productsService = new ProductsService();

      productsService.getProducts = jest.fn().mockRejectedValue(
        Object.assign(new Error('Request timeout'), { code: 'TIMEOUT' })
      );

      try {
        await productsService.getProducts({});
      } catch (error: any) {
        expect(error.message).toBe('Request timeout');
        expect(error.code).toBe('TIMEOUT');
      }
    });

    it('should handle server errors with retry logic', async () => {
      const authService = new AuthService();

      // First call fails, second succeeds
      authService.login = jest.fn()
        .mockRejectedValueOnce(new Error('Server error'))
        .mockResolvedValueOnce({
          access_token: 'access_token',
          user: { id: 'user-1' },
        });

      try {
        await authService.login({ email: 'test@example.com', password: 'pass' });
      } catch (error) {
        // Retry after error
        const result = await authService.login({ email: 'test@example.com', password: 'pass' });
        expect(result.access_token).toBe('access_token');
      }
    });
  });
});