const cartService = require('../../src/services/cartService');
const { Cart, CartItem } = require('../../src/models');

describe('CartService Unit Tests', () => {
  beforeEach(async () => {
    // Clean up database
    await CartItem.destroy({ where: {} });
    await Cart.destroy({ where: {} });
  });

  describe('findOrCreateCart', () => {
    test('should create new cart for new user', async () => {
      const userId = 'new-user-123';
      const cart = await cartService.findOrCreateCart(userId);

      expect(cart).toBeDefined();
      expect(cart.user_id).toBe(userId);
      expect(cart.id).toBeDefined();
      expect(cart.items).toEqual([]);
    });

    test('should return existing cart for existing user', async () => {
      const userId = 'existing-user-456';

      // Create cart first
      const firstCart = await cartService.findOrCreateCart(userId);
      const firstCartId = firstCart.id;

      // Get cart again
      const secondCart = await cartService.findOrCreateCart(userId);

      expect(secondCart.id).toBe(firstCartId);
      expect(secondCart.user_id).toBe(userId);
    });
  });

  describe('addItemToCart', () => {
    test('should add new item to empty cart', async () => {
      const userId = 'test-user-add';
      const productId = 'prod-123';
      const quantity = 2;

      const result = await cartService.addItemToCart(userId, productId, quantity);

      expect(result).toBeDefined();
      expect(result.items).toHaveLength(1);
      expect(result.items[0].product_id).toBe(productId);
      expect(result.items[0].quantity).toBe(quantity);
      expect(result.totals.item_count).toBe(quantity);
    });

    test('should update quantity for existing item', async () => {
      const userId = 'test-user-update';
      const productId = 'prod-123';

      // Add item first time
      await cartService.addItemToCart(userId, productId, 2);

      // Add same item again
      const result = await cartService.addItemToCart(userId, productId, 3);

      expect(result.items).toHaveLength(1);
      expect(result.items[0].quantity).toBe(5); // 2 + 3
      expect(result.totals.item_count).toBe(5);
    });

    test('should throw error for quantity exceeding limit', async () => {
      const userId = 'test-user-limit';
      const productId = 'prod-123';

      await expect(
        cartService.addItemToCart(userId, productId, 15)
      ).rejects.toThrow('Quantity cannot exceed');
    });

    test('should throw error for unavailable product', async () => {
      const userId = 'test-user-unavailable';
      const productId = 'prod-discontinued-999';

      await expect(
        cartService.addItemToCart(userId, productId, 1)
      ).rejects.toThrow('Product is not available');
    });

    test('should throw error for non-existent product', async () => {
      const userId = 'test-user-nonexistent';
      const productId = 'prod-does-not-exist';

      await expect(
        cartService.addItemToCart(userId, productId, 1)
      ).rejects.toThrow('Product not found');
    });
  });

  describe('updateItemQuantity', () => {
    test('should update item quantity successfully', async () => {
      const userId = 'test-user-update-qty';
      const productId = 'prod-123';

      // Add item first
      await cartService.addItemToCart(userId, productId, 2);

      // Update quantity
      const result = await cartService.updateItemQuantity(userId, productId, 5);

      expect(result.items).toHaveLength(1);
      expect(result.items[0].quantity).toBe(5);
      expect(result.totals.item_count).toBe(5);
    });

    test('should throw error for item not in cart', async () => {
      const userId = 'test-user-not-found';
      const productId = 'prod-not-in-cart';

      await expect(
        cartService.updateItemQuantity(userId, productId, 3)
      ).rejects.toThrow('Item not found in cart');
    });

    test('should throw error for invalid quantity', async () => {
      const userId = 'test-user-invalid-qty';
      const productId = 'prod-123';

      // Add item first
      await cartService.addItemToCart(userId, productId, 2);

      await expect(
        cartService.updateItemQuantity(userId, productId, 0)
      ).rejects.toThrow('Quantity must be at least 1');

      await expect(
        cartService.updateItemQuantity(userId, productId, 15)
      ).rejects.toThrow('Quantity cannot exceed');
    });
  });

  describe('removeItemFromCart', () => {
    test('should remove item from cart successfully', async () => {
      const userId = 'test-user-remove';
      const productId1 = 'prod-123';
      const productId2 = 'prod-laptop-123';

      // Add two items
      await cartService.addItemToCart(userId, productId1, 2);
      await cartService.addItemToCart(userId, productId2, 1);

      // Remove one item
      const result = await cartService.removeItemFromCart(userId, productId1);

      expect(result.items).toHaveLength(1);
      expect(result.items[0].product_id).toBe(productId2);
      expect(result.totals.item_count).toBe(1);
    });

    test('should throw error for item not in cart', async () => {
      const userId = 'test-user-remove-not-found';
      const productId = 'prod-not-in-cart';

      await expect(
        cartService.removeItemFromCart(userId, productId)
      ).rejects.toThrow('Item not found in cart');
    });
  });

  describe('clearCart', () => {
    test('should clear all items from cart', async () => {
      const userId = 'test-user-clear';

      // Add multiple items
      await cartService.addItemToCart(userId, 'prod-123', 2);
      await cartService.addItemToCart(userId, 'prod-laptop-123', 1);

      // Clear cart
      const result = await cartService.clearCart(userId);

      expect(result.message).toBe('Cart cleared successfully');
      expect(result.cart_id).toBeDefined();

      // Verify cart is empty
      const cart = await cartService.getCartWithItems(userId);
      expect(cart).toBeNull();
    });
  });

  describe('calculateTotals', () => {
    test('should calculate totals correctly', async () => {
      const enrichedItems = [
        { quantity: 2, subtotal: 59.98 },
        { quantity: 1, subtotal: 1299.99 },
        { quantity: 3, subtotal: 149.97 },
      ];

      const totals = cartService.calculateTotals(enrichedItems);

      expect(totals.item_count).toBe(6);
      expect(totals.total_price).toBe(1509.94);
      expect(totals.currency).toBe('USD');
    });

    test('should handle empty items array', async () => {
      const totals = cartService.calculateTotals([]);

      expect(totals.item_count).toBe(0);
      expect(totals.total_price).toBe(0);
      expect(totals.currency).toBe('USD');
    });
  });

  describe('getCartWithItems', () => {
    test('should return null for empty cart', async () => {
      const userId = 'test-user-empty';
      const result = await cartService.getCartWithItems(userId);

      expect(result).toBeNull();
    });

    test('should return enriched cart data', async () => {
      const userId = 'test-user-enriched';

      // Add item
      await cartService.addItemToCart(userId, 'prod-123', 2);

      // Get cart
      const result = await cartService.getCartWithItems(userId);

      expect(result).toBeDefined();
      expect(result.cart_id).toBeDefined();
      expect(result.user_id).toBe(userId);
      expect(result.items).toHaveLength(1);
      expect(result.items[0].product).toBeDefined();
      expect(result.items[0].subtotal).toBeDefined();
      expect(result.totals).toBeDefined();
      expect(result.created_at).toBeDefined();
      expect(result.updated_at).toBeDefined();
    });
  });
});