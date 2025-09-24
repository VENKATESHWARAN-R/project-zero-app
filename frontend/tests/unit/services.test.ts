/**
 * API service tests
 * Tests all service classes: AuthService, ProductsService, CartService
 */

import { AuthService } from '@/services/auth';
import { ProductsService } from '@/services/products';
import { CartService } from '@/services/cart';
import { authApi, productsApi, cartApi, handleApiCall } from '@/lib/api';

// Mock the API clients and utility functions
jest.mock('@/lib/api');
jest.mock('@/lib/cache');

const mockedAuthApi = authApi as jest.Mocked<typeof authApi>;
const mockedProductsApi = productsApi as jest.Mocked<typeof productsApi>;
const mockedCartApi = cartApi as jest.Mocked<typeof cartApi>;
const mockedHandleApiCall = handleApiCall as jest.MockedFunction<typeof handleApiCall>;

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

// Mock console methods
console.error = jest.fn();

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  describe('login', () => {
    it('should call login API with credentials', async () => {
      const credentials = { email: 'test@example.com', password: 'password' };
      const expectedResponse = {
        access_token: 'access_token_123',
        refresh_token: 'refresh_token_123',
        token_type: 'Bearer',
        expires_in: 3600,
        user: {
          id: '1',
          email: 'test@example.com',
          first_name: 'John',
          last_name: 'Doe',
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
      };

      mockedHandleApiCall.mockResolvedValue(expectedResponse);

      const result = await AuthService.login(credentials);

      expect(mockedHandleApiCall).toHaveBeenCalledWith(
        expect.any(Function),
        'login'
      );
      expect(result).toEqual(expectedResponse);
    });
  });

  describe('register', () => {
    it('should call register API with user data', async () => {
      const userData = {
        email: 'new@example.com',
        password: 'Password123!',
        first_name: 'Jane',
        last_name: 'Smith',
      };
      const expectedResponse = {
        access_token: 'access_token_456',
        refresh_token: 'refresh_token_456',
        token_type: 'Bearer',
        expires_in: 3600,
        user: {
          id: '2',
          email: 'new@example.com',
          first_name: 'Jane',
          last_name: 'Smith',
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
      };

      mockedHandleApiCall.mockResolvedValue(expectedResponse);

      const result = await AuthService.register(userData);

      expect(mockedHandleApiCall).toHaveBeenCalledWith(
        expect.any(Function),
        'register'
      );
      expect(result).toEqual(expectedResponse);
    });
  });

  describe('refreshToken', () => {
    it('should call refresh token API', async () => {
      const refreshToken = 'refresh_token_123';
      const expectedResponse = {
        access_token: 'new_access_token',
        refresh_token: 'new_refresh_token',
        token_type: 'Bearer',
        expires_in: 3600,
      };

      mockedHandleApiCall.mockResolvedValue(expectedResponse);

      const result = await AuthService.refreshToken(refreshToken);

      expect(mockedHandleApiCall).toHaveBeenCalledWith(
        expect.any(Function),
        'refresh token'
      );
      expect(result).toEqual(expectedResponse);
    });
  });

  describe('logout', () => {
    it('should call logout API with refresh token', async () => {
      const refreshToken = 'refresh_token_123';
      const expectedResponse = { message: 'Successfully logged out' };

      mockedHandleApiCall.mockResolvedValue(expectedResponse);

      const result = await AuthService.logout(refreshToken);

      expect(mockedHandleApiCall).toHaveBeenCalledWith(
        expect.any(Function),
        'logout'
      );
      expect(result).toEqual(expectedResponse);
    });
  });

  describe('verifyToken', () => {
    it('should call verify token API', async () => {
      const expectedResponse = {
        valid: true,
        user: {
          id: '1',
          email: 'test@example.com',
          first_name: 'John',
          last_name: 'Doe',
        },
      };

      mockedHandleApiCall.mockResolvedValue(expectedResponse);

      const result = await AuthService.verifyToken();

      expect(mockedHandleApiCall).toHaveBeenCalledWith(
        expect.any(Function),
        'verify token'
      );
      expect(result).toEqual(expectedResponse);
    });
  });

  describe('transformApiUser', () => {
    it('should transform API user to frontend format', () => {
      const apiUser = {
        id: '1',
        email: 'test@example.com',
        first_name: 'John',
        last_name: 'Doe',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
      };

      const result = AuthService.transformApiUser(apiUser);

      expect(result).toEqual({
        id: '1',
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe',
        createdAt: '2023-01-01T00:00:00Z',
        updatedAt: '2023-01-01T00:00:00Z',
      });
    });
  });

  describe('transformToAuthTokens', () => {
    it('should transform login response to auth tokens', () => {
      const response = {
        access_token: 'access_token_123',
        refresh_token: 'refresh_token_123',
        token_type: 'Bearer',
        expires_in: 3600,
        user: {},
      };

      const mockNow = Date.now();
      jest.spyOn(Date, 'now').mockReturnValue(mockNow);

      const result = AuthService.transformToAuthTokens(response);

      expect(result).toEqual({
        accessToken: 'access_token_123',
        refreshToken: 'refresh_token_123',
        tokenType: 'Bearer',
        expiresAt: mockNow + (3600 * 1000),
      });

      jest.restoreAllMocks();
    });
  });

  describe('token storage', () => {
    it('should store tokens in localStorage', () => {
      const tokens = {
        accessToken: 'access_123',
        refreshToken: 'refresh_123',
        tokenType: 'Bearer',
        expiresAt: Date.now() + 3600000,
      };

      AuthService.storeTokens(tokens);

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'auth_tokens',
        JSON.stringify(tokens)
      );
    });

    it('should get tokens from localStorage', () => {
      const tokens = {
        accessToken: 'access_123',
        refreshToken: 'refresh_123',
        tokenType: 'Bearer',
        expiresAt: Date.now() + 3600000,
      };

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(tokens));

      const result = AuthService.getStoredTokens();

      expect(mockLocalStorage.getItem).toHaveBeenCalledWith('auth_tokens');
      expect(result).toEqual(tokens);
    });

    it('should return null for expired tokens', () => {
      const expiredTokens = {
        accessToken: 'access_123',
        refreshToken: 'refresh_123',
        tokenType: 'Bearer',
        expiresAt: Date.now() - 1000, // Expired
      };

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(expiredTokens));

      const result = AuthService.getStoredTokens();

      expect(result).toBeNull();
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_tokens');
    });

    it('should handle invalid JSON gracefully', () => {
      mockLocalStorage.getItem.mockReturnValue('invalid-json');

      const result = AuthService.getStoredTokens();

      expect(result).toBeNull();
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_tokens');
      expect(console.error).toHaveBeenCalled();
    });

    it('should clear tokens from localStorage', () => {
      AuthService.clearTokens();

      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_tokens');
    });
  });

  describe('authentication status', () => {
    it('should return true when authenticated', () => {
      const tokens = {
        accessToken: 'access_123',
        refreshToken: 'refresh_123',
        tokenType: 'Bearer',
        expiresAt: Date.now() + 3600000,
      };

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(tokens));

      const result = AuthService.isAuthenticated();

      expect(result).toBe(true);
    });

    it('should return false when not authenticated', () => {
      mockLocalStorage.getItem.mockReturnValue(null);

      const result = AuthService.isAuthenticated();

      expect(result).toBe(false);
    });
  });

  describe('user management', () => {
    it('should store and get current user', () => {
      const user = {
        id: '1',
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe',
        createdAt: '2023-01-01T00:00:00Z',
        updatedAt: '2023-01-01T00:00:00Z',
      };

      AuthService.storeCurrentUser(user);
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'current_user',
        JSON.stringify(user)
      );

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(user));
      const result = AuthService.getCurrentUser();
      expect(result).toEqual(user);
    });

    it('should clear current user', () => {
      AuthService.clearCurrentUser();

      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('current_user');
    });
  });
});

describe('ProductsService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getProducts', () => {
    it('should call products API with filters', async () => {
      const filters = { category: 'electronics', page: 1 };
      const expectedResponse = {
        products: [],
        total: 0,
        page: 1,
        limit: 20,
        total_pages: 0,
      };

      mockedHandleApiCall.mockResolvedValue(expectedResponse);

      const result = await ProductsService.getProducts(filters);

      expect(mockedHandleApiCall).toHaveBeenCalledWith(
        expect.any(Function),
        'get products'
      );
      expect(result).toEqual(expectedResponse);
    });
  });

  describe('getProduct', () => {
    it('should call single product API', async () => {
      const productId = 'prod_123';
      const expectedProduct = {
        id: 'prod_123',
        name: 'Test Product',
        price: 1999,
        image_url: 'test.jpg',
      };

      mockedHandleApiCall.mockResolvedValue(expectedProduct);

      await ProductsService.getProduct(productId);

      expect(mockedHandleApiCall).toHaveBeenCalledWith(
        expect.any(Function),
        'get product prod_123'
      );
    });
  });

  describe('formatPrice', () => {
    it('should format price correctly', () => {
      expect(ProductsService.formatPrice(1999)).toBe('$19.99');
      expect(ProductsService.formatPrice(50000, 'EUR')).toBe('€500.00');
    });
  });

  describe('product availability', () => {
    const inStockProduct = {
      id: '1',
      name: 'Test',
      inStock: true,
      stockQuantity: 10,
      price: 1000,
      currency: 'USD',
      category: 'test',
      imageUrl: 'test.jpg',
      images: ['test.jpg'],
      description: 'Test product',
      specifications: {},
      createdAt: '2023-01-01',
      updatedAt: '2023-01-01',
    };

    const outOfStockProduct = { ...inStockProduct, inStock: false, stockQuantity: 0 };
    const lowStockProduct = { ...inStockProduct, stockQuantity: 3 };

    it('should check product availability correctly', () => {
      expect(ProductsService.isProductAvailable(inStockProduct)).toBe(true);
      expect(ProductsService.isProductAvailable(outOfStockProduct)).toBe(false);
    });

    it('should get availability text', () => {
      expect(ProductsService.getAvailabilityText(inStockProduct)).toBe('In stock');
      expect(ProductsService.getAvailabilityText(outOfStockProduct)).toBe('Out of stock');
      expect(ProductsService.getAvailabilityText(lowStockProduct)).toBe('Only 3 left');
    });

    it('should get availability status', () => {
      expect(ProductsService.getAvailabilityStatus(inStockProduct)).toBe('available');
      expect(ProductsService.getAvailabilityStatus(outOfStockProduct)).toBe('out-of-stock');
      expect(ProductsService.getAvailabilityStatus(lowStockProduct)).toBe('low-stock');
    });
  });

  describe('product filtering', () => {
    const products = [
      {
        id: '1', name: 'Laptop', category: 'electronics', price: 99999,
        inStock: true, stockQuantity: 5, currency: 'USD', imageUrl: 'laptop.jpg',
        images: ['laptop.jpg'], description: 'Gaming laptop', specifications: {},
        createdAt: '2023-01-01', updatedAt: '2023-01-01',
      },
      {
        id: '2', name: 'Phone', category: 'electronics', price: 79999,
        inStock: false, stockQuantity: 0, currency: 'USD', imageUrl: 'phone.jpg',
        images: ['phone.jpg'], description: 'Smart phone', specifications: {},
        createdAt: '2023-01-02', updatedAt: '2023-01-02',
      },
      {
        id: '3', name: 'Book', category: 'books', price: 1999,
        inStock: true, stockQuantity: 20, currency: 'USD', imageUrl: 'book.jpg',
        images: ['book.jpg'], description: 'Programming book', specifications: {},
        createdAt: '2023-01-03', updatedAt: '2023-01-03',
      },
    ];

    it('should filter by category', () => {
      const result = ProductsService.filterByCategory(products, 'electronics');
      expect(result).toHaveLength(2);
      expect(result[0].category).toBe('electronics');
    });

    it('should filter by price range', () => {
      const result = ProductsService.filterByPriceRange(products, 50000, 80000);
      expect(result).toHaveLength(1);
      expect(result[0].name).toBe('Phone');
    });

    it('should filter by availability', () => {
      const result = ProductsService.filterByAvailability(products, true);
      expect(result).toHaveLength(2);
      expect(result.every(p => p.inStock)).toBe(true);
    });
  });

  describe('product sorting', () => {
    const products = [
      { id: '1', name: 'Zebra', price: 1000, createdAt: '2023-01-03' },
      { id: '2', name: 'Apple', price: 3000, createdAt: '2023-01-01' },
      { id: '3', name: 'Banana', price: 2000, createdAt: '2023-01-02' },
    ] as any[];

    it('should sort by name ascending', () => {
      const result = ProductsService.sortProducts(products, 'name', 'asc');
      expect(result.map(p => p.name)).toEqual(['Apple', 'Banana', 'Zebra']);
    });

    it('should sort by price descending', () => {
      const result = ProductsService.sortProducts(products, 'price', 'desc');
      expect(result.map(p => p.price)).toEqual([3000, 2000, 1000]);
    });

    it('should sort by creation date', () => {
      const result = ProductsService.sortProducts(products, 'created_at', 'asc');
      expect(result.map(p => p.id)).toEqual(['2', '3', '1']);
    });
  });

  describe('utility functions', () => {
    const products = [
      { id: '1', name: 'Gaming Laptop', description: 'High performance gaming', category: 'electronics', price: 150000 },
      { id: '2', name: 'Office Mouse', description: 'Wireless mouse for office', category: 'electronics', price: 2999 },
      { id: '3', name: 'Programming Book', description: 'Learn to code', category: 'books', price: 4999 },
    ] as any[];

    it('should search products locally', () => {
      const result = ProductsService.searchProductsLocally(products, 'gaming');
      expect(result).toHaveLength(1);
      expect(result[0].name).toBe('Gaming Laptop');
    });

    it('should get unique categories', () => {
      const result = ProductsService.getUniqueCategories(products);
      expect(result).toEqual(['books', 'electronics']);
    });

    it('should get price range', () => {
      const result = ProductsService.getPriceRange(products);
      expect(result).toEqual({ min: 2999, max: 150000 });
    });

    it('should handle empty products array', () => {
      const result = ProductsService.getPriceRange([]);
      expect(result).toEqual({ min: 0, max: 0 });
    });
  });

  describe('transformProductFromApi', () => {
    it('should transform API product correctly', () => {
      const apiProduct = {
        id: '1',
        name: 'Test Product',
        description: 'Test description',
        price: 1999,
        currency: 'USD',
        category: 'electronics',
        image_url: 'test.jpg',
        images: ['test1.jpg', 'test2.jpg'],
        in_stock: true,
        stock_quantity: 10,
        specifications: { color: 'black' },
        created_at: '2023-01-01',
        updated_at: '2023-01-02',
      };

      const result = ProductsService.transformProductFromApi(apiProduct);

      expect(result).toEqual({
        id: '1',
        name: 'Test Product',
        description: 'Test description',
        price: 1999,
        currency: 'USD',
        category: 'electronics',
        imageUrl: 'test.jpg',
        images: ['test1.jpg', 'test2.jpg'],
        inStock: true,
        stockQuantity: 10,
        specifications: { color: 'black' },
        createdAt: '2023-01-01',
        updatedAt: '2023-01-02',
      });
    });
  });
});

describe('CartService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('API methods', () => {
    it('should get cart', async () => {
      const expectedCart = { id: '1', items: [], totalAmount: 0 };
      mockedHandleApiCall.mockResolvedValue(expectedCart);

      const result = await CartService.getCart();

      expect(mockedHandleApiCall).toHaveBeenCalledWith(
        expect.any(Function),
        'get cart'
      );
      expect(result).toEqual(expectedCart);
    });

    it('should add to cart', async () => {
      const expectedItem = { id: '1', productId: 'prod_1', quantity: 2 };
      mockedHandleApiCall.mockResolvedValue(expectedItem);

      const result = await CartService.addToCart('prod_1', 2);

      expect(mockedHandleApiCall).toHaveBeenCalledWith(
        expect.any(Function),
        'add to cart: prod_1'
      );
      expect(result).toEqual(expectedItem);
    });

    it('should update cart item', async () => {
      const expectedItem = { id: 'item_1', productId: 'prod_1', quantity: 3 };
      mockedHandleApiCall.mockResolvedValue(expectedItem);

      const result = await CartService.updateCartItem('item_1', 3);

      expect(mockedHandleApiCall).toHaveBeenCalledWith(
        expect.any(Function),
        'update cart item: item_1'
      );
      expect(result).toEqual(expectedItem);
    });

    it('should remove from cart', async () => {
      const expectedResponse = {
        message: 'Item removed',
        removed_item_id: 'item_1',
        cart_summary: { itemCount: 0, totalAmount: 0 },
      };
      mockedHandleApiCall.mockResolvedValue(expectedResponse);

      const result = await CartService.removeFromCart('item_1');

      expect(mockedHandleApiCall).toHaveBeenCalledWith(
        expect.any(Function),
        'remove from cart: item_1'
      );
      expect(result).toEqual(expectedResponse);
    });

    it('should clear cart', async () => {
      const expectedResponse = {
        message: 'Cart cleared',
        cart_summary: { itemCount: 0, totalAmount: 0 },
      };
      mockedHandleApiCall.mockResolvedValue(expectedResponse);

      const result = await CartService.clearCart();

      expect(mockedHandleApiCall).toHaveBeenCalledWith(
        expect.any(Function),
        'clear cart'
      );
      expect(result).toEqual(expectedResponse);
    });
  });

  describe('cart calculations', () => {
    const cartItems = [
      {
        id: '1',
        productId: 'prod_1',
        quantity: 2,
        addedAt: '2023-01-01',
        product: { id: 'prod_1', name: 'Item 1', price: 1000 } as any,
      },
      {
        id: '2',
        productId: 'prod_2',
        quantity: 1,
        addedAt: '2023-01-01',
        product: { id: 'prod_2', name: 'Item 2', price: 1500 } as any,
      },
    ];

    it('should calculate total correctly', () => {
      const result = CartService.calculateTotal(cartItems);
      expect(result).toBe(3500); // (2 * 1000) + (1 * 1500)
    });

    it('should calculate item count correctly', () => {
      const result = CartService.calculateItemCount(cartItems);
      expect(result).toBe(3); // 2 + 1
    });

    it('should format cart total', () => {
      const result = CartService.formatCartTotal(3500);
      expect(result).toBe('$35.00');
    });
  });

  describe('cart validation', () => {
    const mockCart = {
      id: '1',
      userId: 'user_1',
      items: [
        {
          id: '1',
          productId: 'prod_1',
          quantity: 2,
          addedAt: '2023-01-01',
          product: {
            id: 'prod_1',
            name: 'Item 1',
            price: 1000,
            inStock: true,
            stockQuantity: 5,
          } as any,
        },
      ],
      totalAmount: 2000,
      itemCount: 2,
      currency: 'USD',
      createdAt: '2023-01-01',
      updatedAt: '2023-01-01',
    };

    it('should detect empty cart', () => {
      const emptyCart = { ...mockCart, items: [], itemCount: 0 };
      expect(CartService.isEmpty(emptyCart)).toBe(true);
      expect(CartService.isEmpty(mockCart)).toBe(false);
    });

    it('should validate stock availability', () => {
      expect(CartService.hasValidStock(mockCart)).toBe(true);

      const invalidCart = {
        ...mockCart,
        items: [
          {
            ...mockCart.items[0],
            product: { ...mockCart.items[0].product, stockQuantity: 1 },
          },
        ],
      };
      expect(CartService.hasValidStock(invalidCart)).toBe(false);
    });

    it('should find items with insufficient stock', () => {
      const invalidCart = {
        ...mockCart,
        items: [
          {
            ...mockCart.items[0],
            quantity: 10,
            product: { ...mockCart.items[0].product, stockQuantity: 5 },
          },
        ],
      };

      const result = CartService.getItemsWithInsufficientStock(invalidCart);
      expect(result).toHaveLength(1);
    });

    it('should find item by product ID', () => {
      const result = CartService.findItemByProductId(mockCart, 'prod_1');
      expect(result).toBeDefined();
      expect(result!.productId).toBe('prod_1');

      const notFound = CartService.findItemByProductId(mockCart, 'prod_999');
      expect(notFound).toBeUndefined();
    });

    it('should check if product is in cart', () => {
      expect(CartService.isProductInCart(mockCart, 'prod_1')).toBe(true);
      expect(CartService.isProductInCart(mockCart, 'prod_999')).toBe(false);
    });

    it('should calculate max quantity for product', () => {
      const result = CartService.getMaxQuantityForProduct(mockCart, 'prod_1', 10);
      expect(result).toBe(8); // 10 - 2 (current quantity)

      const newProduct = CartService.getMaxQuantityForProduct(mockCart, 'prod_new', 5);
      expect(newProduct).toBe(5);
    });
  });

  describe('add to cart validation', () => {
    const mockCart = {
      id: '1',
      items: Array(49).fill(null).map((_, i) => ({
        id: `item_${i}`,
        productId: `prod_${i}`,
        quantity: 1,
        addedAt: '2023-01-01',
        product: { id: `prod_${i}`, stockQuantity: 10 } as any,
      })),
    } as any;

    it('should validate successful add to cart', () => {
      const result = CartService.validateAddToCart(mockCart, 'new_product', 2, 10);
      expect(result.valid).toBe(true);
    });

    it('should reject zero or negative quantity', () => {
      const result = CartService.validateAddToCart(mockCart, 'prod_1', 0, 10);
      expect(result.valid).toBe(false);
      expect(result.message).toBe('Quantity must be greater than 0');
    });

    it('should reject excessive quantity', () => {
      const result = CartService.validateAddToCart(mockCart, 'prod_1', 11, 20);
      expect(result.valid).toBe(false);
      expect(result.message).toBe('Maximum quantity per item is 10');
    });

    it('should reject when not enough stock', () => {
      const result = CartService.validateAddToCart(mockCart, 'prod_1', 5, 3);
      expect(result.valid).toBe(false);
      expect(result.message).toBe('Not enough stock available');
    });

    it('should reject when cart is full', () => {
      const fullCart = {
        ...mockCart,
        items: Array(50).fill(null).map((_, i) => ({
          id: `item_${i}`,
          productId: `prod_${i}`,
        })),
      } as any;

      const result = CartService.validateAddToCart(fullCart, 'new_product', 1, 10);
      expect(result.valid).toBe(false);
      expect(result.message).toBe('Maximum 50 unique items allowed per cart');
    });
  });

  describe('data transformation', () => {
    it('should transform cart item from API', () => {
      const apiItem = {
        id: '1',
        product_id: 'prod_1',
        quantity: 2,
        added_at: '2023-01-01',
        product: {
          id: 'prod_1',
          name: 'Test Product',
          price: 1999,
          currency: 'USD',
          image_url: 'test.jpg',
          in_stock: true,
          stock_quantity: 10,
        },
      };

      const result = CartService.transformCartItemFromApi(apiItem);

      expect(result).toEqual({
        id: '1',
        productId: 'prod_1',
        quantity: 2,
        addedAt: '2023-01-01',
        product: {
          id: 'prod_1',
          name: 'Test Product',
          price: 1999,
          currency: 'USD',
          imageUrl: 'test.jpg',
          inStock: true,
          stockQuantity: 10,
          description: '',
          category: '',
          images: ['test.jpg'],
          specifications: {},
          createdAt: '',
          updatedAt: '',
        },
      });
    });

    it('should transform cart from API', () => {
      const apiCart = {
        id: '1',
        user_id: 'user_1',
        items: [],
        total_amount: 0,
        item_count: 0,
        currency: 'USD',
        created_at: '2023-01-01',
        updated_at: '2023-01-01',
      };

      const result = CartService.transformCartFromApi(apiCart);

      expect(result).toEqual({
        id: '1',
        userId: 'user_1',
        items: [],
        totalAmount: 0,
        itemCount: 0,
        currency: 'USD',
        createdAt: '2023-01-01',
        updatedAt: '2023-01-01',
      });
    });
  });

  describe('cart storage', () => {
    const mockCart = {
      id: '1',
      userId: 'user_1',
      items: [],
      totalAmount: 0,
      itemCount: 0,
      currency: 'USD',
      createdAt: '2023-01-01',
      updatedAt: '2023-01-01',
    };

    it('should get correct storage key', () => {
      expect(CartService.getCartStorageKey('user_1')).toBe('cart_user_1');
      expect(CartService.getCartStorageKey()).toBe('cart_guest');
    });

    it('should save cart to storage', () => {
      CartService.saveCartToStorage(mockCart, 'user_1');

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'cart_user_1',
        JSON.stringify(mockCart)
      );
    });

    it('should load cart from storage', () => {
      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(mockCart));

      const result = CartService.loadCartFromStorage('user_1');

      expect(mockLocalStorage.getItem).toHaveBeenCalledWith('cart_user_1');
      expect(result).toEqual(mockCart);
    });

    it('should handle storage errors gracefully', () => {
      mockLocalStorage.setItem.mockImplementation(() => {
        throw new Error('Storage full');
      });

      CartService.saveCartToStorage(mockCart);

      expect(console.error).toHaveBeenCalledWith(
        'Failed to save cart to storage:',
        expect.any(Error)
      );
    });

    it('should clear cart from storage', () => {
      CartService.clearCartFromStorage('user_1');

      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('cart_user_1');
    });
  });
});