/**
 * Cart service client
 * Handles all cart management API calls
 */

import { cartApi, handleApiCall } from '@/lib/api';
import { Cart, CartItem, CartSummary, AddToCartRequest, UpdateCartItemRequest, BulkAddToCartRequest, CartValidationResponse, CartResponse } from '@/types/cart';

type ApiCartProduct = CartResponse['items'][number]['product'] & {
  description?: string;
  category?: string;
  images?: string[];
  specifications?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
};

type ApiCartItem = Omit<CartResponse['items'][number], 'product'> & {
  product: ApiCartProduct;
};

export class CartService {
  /**
   * Get current user's cart with all items
   */
  static async getCart(): Promise<CartResponse> {
    return handleApiCall(
      () => cartApi.get<CartResponse>('/cart'),
      'get cart'
    );
  }

  /**
   * Get cart summary for header display
   */
  static async getCartSummary(): Promise<CartSummary> {
    return handleApiCall(
      () => cartApi.get<CartSummary>('/cart/summary'),
      'get cart summary'
    );
  }

  /**
   * Add a product to cart or update quantity if already exists
   */
  static async addToCart(productId: string, quantity: number): Promise<CartItem> {
    const request: AddToCartRequest = {
      product_id: productId,
      quantity: quantity
    };

    return handleApiCall(
      () => cartApi.post<CartItem>('/cart/items', request),
      `add to cart: ${productId}`
    );
  }

  /**
   * Update quantity of specific cart item
   */
  static async updateCartItem(itemId: string, quantity: number): Promise<CartItem> {
    const request: UpdateCartItemRequest = {
      quantity: quantity
    };

    return handleApiCall(
      () => cartApi.put<CartItem>(`/cart/items/${itemId}`, request),
      `update cart item: ${itemId}`
    );
  }

  /**
   * Remove specific item from cart
   */
  static async removeFromCart(itemId: string): Promise<{ message: string; removed_item_id: string; cart_summary: CartSummary }> {
    return handleApiCall(
      () => cartApi.delete(`/cart/items/${itemId}`),
      `remove from cart: ${itemId}`
    );
  }

  /**
   * Clear all items from cart
   */
  static async clearCart(): Promise<{ message: string; cart_summary: CartSummary }> {
    return handleApiCall(
      () => cartApi.delete('/cart'),
      'clear cart'
    );
  }

  /**
   * Add multiple products to cart in single request
   */
  static async addBulkToCart(items: { product_id: string; quantity: number }[]): Promise<{
    added_items: Array<{ id: string; product_id: string; quantity: number; status: string }>;
    failed_items: Array<{ product_id: string; error: string }>;
    cart_summary: CartSummary;
  }> {
    const request: BulkAddToCartRequest = { items };

    return handleApiCall(
      () => cartApi.post('/cart/items/bulk', request),
      'bulk add to cart'
    );
  }

  /**
   * Validate cart items against current product availability and pricing
   */
  static async validateCart(): Promise<CartValidationResponse> {
    return handleApiCall(
      () => cartApi.post<CartValidationResponse>('/cart/validate'),
      'validate cart'
    );
  }

  /**
   * Calculate total price of cart items
   */
  static calculateTotal(items: CartItem[]): number {
    return items.reduce((total, item) => {
      return total + (item.product.price * item.quantity);
    }, 0);
  }

  /**
   * Calculate total item count in cart
   */
  static calculateItemCount(items: CartItem[]): number {
    return items.reduce((count, item) => count + item.quantity, 0);
  }

  /**
   * Format cart total as currency
   */
  static formatCartTotal(totalInCents: number, currency: string = 'USD'): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(totalInCents / 100);
  }

  /**
   * Check if cart is empty
   */
  static isEmpty(cart: Cart): boolean {
    return cart.items.length === 0 || cart.itemCount === 0;
  }

  /**
   * Check if cart has sufficient stock for all items
   */
  static hasValidStock(cart: Cart): boolean {
    return cart.items.every(item =>
      item.product.inStock && item.quantity <= item.product.stockQuantity
    );
  }

  /**
   * Get items with insufficient stock
   */
  static getItemsWithInsufficientStock(cart: Cart): CartItem[] {
    return cart.items.filter(item =>
      !item.product.inStock || item.quantity > item.product.stockQuantity
    );
  }

  /**
   * Find cart item by product ID
   */
  static findItemByProductId(cart: Cart, productId: string): CartItem | undefined {
    return cart.items.find(item => item.productId === productId);
  }

  /**
   * Check if product is already in cart
   */
  static isProductInCart(cart: Cart, productId: string): boolean {
    return cart.items.some(item => item.productId === productId);
  }

  /**
   * Get maximum quantity that can be added for a product
   */
  static getMaxQuantityForProduct(cart: Cart, productId: string, stockQuantity: number): number {
    const existingItem = this.findItemByProductId(cart, productId);
    const currentQuantity = existingItem ? existingItem.quantity : 0;
    return Math.max(0, stockQuantity - currentQuantity);
  }

  /**
   * Validate add to cart request
   */
  static validateAddToCart(
    cart: Cart,
    productId: string,
    quantity: number,
    stockQuantity: number
  ): { valid: boolean; message?: string } {
    if (quantity <= 0) {
      return { valid: false, message: 'Quantity must be greater than 0' };
    }

    if (quantity > 10) {
      return { valid: false, message: 'Maximum quantity per item is 10' };
    }

    const existingItem = this.findItemByProductId(cart, productId);
    const currentQuantity = existingItem ? existingItem.quantity : 0;
    const totalQuantity = currentQuantity + quantity;

    if (totalQuantity > stockQuantity) {
      return { valid: false, message: 'Not enough stock available' };
    }

    if (cart.items.length >= 50 && !existingItem) {
      return { valid: false, message: 'Maximum 50 unique items allowed per cart' };
    }

    return { valid: true };
  }

  /**
   * Transform API cart item to frontend interface
   */
  static transformCartItemFromApi(apiItem: ApiCartItem): CartItem {
    return {
      id: apiItem.id,
      productId: apiItem.product_id,
      quantity: apiItem.quantity,
      addedAt: apiItem.added_at,
      product: {
        id: apiItem.product.id,
        name: apiItem.product.name,
        price: apiItem.product.price,
        currency: apiItem.product.currency,
        imageUrl: apiItem.product.image_url,
        inStock: apiItem.product.in_stock,
        stockQuantity: apiItem.product.stock_quantity,
        description: apiItem.product.description || '',
        category: apiItem.product.category || '',
        images: apiItem.product.images || [apiItem.product.image_url],
        specifications: apiItem.product.specifications || {},
        createdAt: apiItem.product.created_at || '',
        updatedAt: apiItem.product.updated_at || '',
      }
    };
  }

  /**
   * Transform API cart response to frontend interface
   */
  static transformCartFromApi(apiCart: CartResponse): Cart {
    return {
      id: apiCart.id,
      userId: apiCart.user_id,
      items: apiCart.items.map(item => this.transformCartItemFromApi(item as ApiCartItem)),
      totalAmount: apiCart.total_amount,
      itemCount: apiCart.item_count,
      currency: apiCart.currency,
      createdAt: apiCart.created_at,
      updatedAt: apiCart.updated_at,
    };
  }

  /**
   * Get cart persistence key for localStorage
   */
  static getCartStorageKey(userId?: string): string {
    return userId ? `cart_${userId}` : 'cart_guest';
  }

  /**
   * Save cart to localStorage for offline access
   */
  static saveCartToStorage(cart: Cart, userId?: string): void {
    try {
      const key = this.getCartStorageKey(userId);
      localStorage.setItem(key, JSON.stringify(cart));
    } catch (error) {
      console.error('Failed to save cart to storage:', error);
    }
  }

  /**
   * Load cart from localStorage
   */
  static loadCartFromStorage(userId?: string): Cart | null {
    try {
      const key = this.getCartStorageKey(userId);
      const cartStr = localStorage.getItem(key);
      return cartStr ? JSON.parse(cartStr) : null;
    } catch (error) {
      console.error('Failed to load cart from storage:', error);
      return null;
    }
  }

  /**
   * Clear cart from localStorage
   */
  static clearCartFromStorage(userId?: string): void {
    try {
      const key = this.getCartStorageKey(userId);
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to clear cart from storage:', error);
    }
  }
}

export default CartService;
