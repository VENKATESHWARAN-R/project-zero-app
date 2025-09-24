/**
 * Cart API Contract Tests
 * These tests verify that our cart service client correctly implements the API contract
 * Based on: /specs/004-build-a-next/contracts/cart-api.md
 */

import { CartService } from '@/services/cart';

describe('Cart API Contract', () => {
  let cartService: CartService;

  beforeEach(() => {
    cartService = new CartService();
  });

  describe('GET /cart', () => {
    it('should retrieve user cart with items', async () => {
      const response = await cartService.getCart();

      expect(response).toMatchObject({
        id: expect.any(String),
        user_id: expect.any(String),
        items: expect.arrayContaining([
          expect.objectContaining({
            id: expect.any(String),
            product_id: expect.any(String),
            quantity: expect.any(Number),
            added_at: expect.any(String),
            product: expect.objectContaining({
              id: expect.any(String),
              name: expect.any(String),
              price: expect.any(Number),
              currency: 'USD',
              image_url: expect.any(String),
              in_stock: expect.any(Boolean),
              stock_quantity: expect.any(Number),
            }),
          }),
        ]),
        total_amount: expect.any(Number),
        item_count: expect.any(Number),
        currency: 'USD',
        created_at: expect.any(String),
        updated_at: expect.any(String),
      });
    });

    it('should handle empty cart', async () => {
      const response = await cartService.getCart();

      expect(response).toMatchObject({
        id: expect.any(String),
        user_id: expect.any(String),
        items: [],
        total_amount: 0,
        item_count: 0,
        currency: 'USD',
      });
    });
  });

  describe('POST /cart/items', () => {
    it('should add item to cart successfully', async () => {
      const itemData = {
        product_id: 'product-uuid-123',
        quantity: 1,
      };

      const response = await cartService.addItem(itemData);

      expect(response).toMatchObject({
        id: expect.any(String),
        product_id: 'product-uuid-123',
        quantity: 1,
        added_at: expect.any(String),
        product: expect.objectContaining({
          id: 'product-uuid-123',
          name: expect.any(String),
          price: expect.any(Number),
          currency: 'USD',
        }),
        cart_summary: {
          total_amount: expect.any(Number),
          item_count: expect.any(Number),
        },
      });
    });

    it('should handle insufficient stock with 409', async () => {
      const itemData = {
        product_id: 'low-stock-product',
        quantity: 100,
      };

      await expect(cartService.addItem(itemData)).rejects.toThrow('Insufficient stock');
    });
  });

  describe('PUT /cart/items/{id}', () => {
    it('should update cart item quantity', async () => {
      const itemId = 'cart-item-uuid-1';
      const updateData = { quantity: 3 };

      const response = await cartService.updateItem(itemId, updateData);

      expect(response).toMatchObject({
        id: itemId,
        quantity: 3,
        cart_summary: {
          total_amount: expect.any(Number),
          item_count: expect.any(Number),
        },
      });
    });

    it('should handle item not found with 404', async () => {
      const invalidItemId = 'nonexistent-item';
      const updateData = { quantity: 2 };

      await expect(cartService.updateItem(invalidItemId, updateData)).rejects.toThrow(
        'Cart item not found'
      );
    });
  });

  describe('DELETE /cart/items/{id}', () => {
    it('should remove item from cart', async () => {
      const itemId = 'cart-item-uuid-1';

      const response = await cartService.removeItem(itemId);

      expect(response).toMatchObject({
        message: 'Item removed from cart',
        removed_item_id: itemId,
        cart_summary: {
          total_amount: expect.any(Number),
          item_count: expect.any(Number),
        },
      });
    });
  });

  describe('DELETE /cart', () => {
    it('should clear all items from cart', async () => {
      const response = await cartService.clearCart();

      expect(response).toMatchObject({
        message: 'Cart cleared successfully',
        cart_summary: {
          total_amount: 0,
          item_count: 0,
        },
      });
    });
  });

  describe('GET /cart/summary', () => {
    it('should get cart summary for header display', async () => {
      const response = await cartService.getCartSummary();

      expect(response).toMatchObject({
        item_count: expect.any(Number),
        total_amount: expect.any(Number),
        currency: 'USD',
        updated_at: expect.any(String),
      });
    });
  });

  describe('POST /cart/validate', () => {
    it('should validate cart items successfully', async () => {
      const response = await cartService.validateCart();

      expect(response).toMatchObject({
        valid: expect.any(Boolean),
        items: expect.arrayContaining([
          expect.objectContaining({
            cart_item_id: expect.any(String),
            product_id: expect.any(String),
            status: expect.any(String),
            requested_quantity: expect.any(Number),
            available_quantity: expect.any(Number),
            current_price: expect.any(Number),
            price_changed: expect.any(Boolean),
          }),
        ]),
        total_amount: expect.any(Number),
        issues: expect.any(Array),
      });
    });

    it('should handle validation issues', async () => {
      const response = await cartService.validateCart();

      if (!response.valid) {
        expect(response.issues).toEqual(
          expect.arrayContaining([
            expect.objectContaining({
              type: expect.any(String),
              cart_item_id: expect.any(String),
              message: expect.any(String),
            }),
          ])
        );
      }
    });
  });

  describe('POST /cart/items/bulk', () => {
    it('should add multiple items to cart', async () => {
      const bulkData = {
        items: [
          { product_id: 'product-uuid-123', quantity: 2 },
          { product_id: 'product-uuid-456', quantity: 1 },
        ],
      };

      const response = await cartService.addBulkItems(bulkData);

      expect(response).toMatchObject({
        added_items: expect.arrayContaining([
          expect.objectContaining({
            id: expect.any(String),
            product_id: expect.any(String),
            quantity: expect.any(Number),
            status: 'added',
          }),
        ]),
        failed_items: expect.any(Array),
        cart_summary: {
          total_amount: expect.any(Number),
          item_count: expect.any(Number),
        },
      });
    });
  });
});