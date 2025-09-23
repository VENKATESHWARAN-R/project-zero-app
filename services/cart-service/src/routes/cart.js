const express = require('express');
const cartService = require('../services/cartService');
const authMiddleware = require('../middleware/auth');
const {
  validateAddItem,
  validateUpdateQuantity,
  validateRemoveItem,
} = require('../middleware/validation');
const logger = require('../services/logger');

const router = express.Router();

// POST /cart/add - Add item to cart
router.post('/add', authMiddleware, validateAddItem, async (req, res, next) => {
  try {
    const { product_id, quantity } = req.body;
    const userId = req.user.id;

    logger.cartOperation('add_item', userId, null, {
      correlationId: req.correlationId,
      productId: product_id,
      quantity,
    });

    const cartResponse = await cartService.addItemToCart(
      userId,
      product_id,
      quantity
    );

    logger.cartOperation('add_item_success', userId, cartResponse.cart_id, {
      correlationId: req.correlationId,
      productId: product_id,
      quantity,
      totalItems: cartResponse.totals.item_count,
    });

    res.json(cartResponse);
  } catch (error) {
    next(error);
  }
});

// GET /cart - Get cart contents
router.get('/', authMiddleware, async (req, res, next) => {
  try {
    const userId = req.user.id;

    logger.cartOperation('get_cart', userId, null, {
      correlationId: req.correlationId,
    });

    const cartResponse = await cartService.getCartWithItems(userId);

    if (!cartResponse) {
      logger.cartOperation('get_cart_empty', userId, null, {
        correlationId: req.correlationId,
      });

      return res.status(404).json({
        message: 'Cart is empty',
        cart_id: null,
        items: [],
        totals: {
          item_count: 0,
          total_price: 0.0,
          currency: 'USD',
        },
      });
    }

    logger.cartOperation('get_cart_success', userId, cartResponse.cart_id, {
      correlationId: req.correlationId,
      itemCount: cartResponse.items.length,
      totalItems: cartResponse.totals.item_count,
    });

    res.json(cartResponse);
  } catch (error) {
    next(error);
  }
});

// PUT /cart/items/:product_id - Update item quantity
router.put(
  '/items/:product_id',
  authMiddleware,
  validateUpdateQuantity,
  async (req, res, next) => {
    try {
      const { product_id } = req.params;
      const { quantity } = req.body;
      const userId = req.user.id;

      logger.cartOperation('update_item', userId, null, {
        correlationId: req.correlationId,
        productId: product_id,
        newQuantity: quantity,
      });

      const cartResponse = await cartService.updateItemQuantity(
        userId,
        product_id,
        quantity
      );

      logger.cartOperation(
        'update_item_success',
        userId,
        cartResponse.cart_id,
        {
          correlationId: req.correlationId,
          productId: product_id,
          newQuantity: quantity,
          totalItems: cartResponse.totals.item_count,
        }
      );

      res.json(cartResponse);
    } catch (error) {
      next(error);
    }
  }
);

// DELETE /cart/items/:product_id - Remove item from cart
router.delete(
  '/items/:product_id',
  authMiddleware,
  validateRemoveItem,
  async (req, res, next) => {
    try {
      const { product_id } = req.params;
      const userId = req.user.id;

      logger.cartOperation('remove_item', userId, null, {
        correlationId: req.correlationId,
        productId: product_id,
      });

      const cartResponse = await cartService.removeItemFromCart(
        userId,
        product_id
      );

      if (cartResponse) {
        logger.cartOperation(
          'remove_item_success',
          userId,
          cartResponse.cart_id,
          {
            correlationId: req.correlationId,
            productId: product_id,
            remainingItems: cartResponse.totals.item_count,
          }
        );

        res.json(cartResponse);
      } else {
        // Cart is now empty
        logger.cartOperation('remove_item_cart_empty', userId, null, {
          correlationId: req.correlationId,
          productId: product_id,
        });

        res.json({
          cart_id: null,
          user_id: userId,
          items: [],
          totals: {
            item_count: 0,
            total_price: 0.0,
            currency: 'USD',
          },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      }
    } catch (error) {
      next(error);
    }
  }
);

// DELETE /cart - Clear entire cart
router.delete('/', authMiddleware, async (req, res, next) => {
  try {
    const userId = req.user.id;

    logger.cartOperation('clear_cart', userId, null, {
      correlationId: req.correlationId,
    });

    const clearResponse = await cartService.clearCart(userId);

    logger.cartOperation('clear_cart_success', userId, clearResponse.cart_id, {
      correlationId: req.correlationId,
    });

    res.json(clearResponse);
  } catch (error) {
    next(error);
  }
});

module.exports = router;
