const { Cart, CartItem } = require('../models');
const productService = require('./productService');

class CartService {
  constructor() {
    this.maxQuantityPerItem = parseInt(
      process.env.MAX_QUANTITY_PER_ITEM || '10'
    );
    this.maxTotalItems = 50; // Configurable cart limit
  }

  async findOrCreateCart(userId) {
    let cart = await Cart.findOne({
      where: { user_id: userId },
      include: [
        {
          model: CartItem,
          as: 'items',
        },
      ],
    });

    if (!cart) {
      cart = await Cart.create({
        user_id: userId,
      });
      cart.items = [];
    }

    return cart;
  }

  async addItemToCart(userId, productId, quantity) {
    if (quantity > this.maxQuantityPerItem) {
      throw new Error(
        `Quantity cannot exceed ${this.maxQuantityPerItem} per item`
      );
    }

    // Validate product exists and is available
    const product = await productService.getProduct(productId);
    if (!product) {
      throw new Error('Product not found');
    }

    if (product.availability === false) {
      throw new Error('Product is not available');
    }

    const cart = await this.findOrCreateCart(userId);

    // Check if item already exists in cart
    let cartItem = await CartItem.findOne({
      where: {
        cart_id: cart.id,
        product_id: productId,
      },
    });

    if (cartItem) {
      // Update existing item quantity
      const newQuantity = cartItem.quantity + quantity;
      if (newQuantity > this.maxQuantityPerItem) {
        throw new Error(
          `Total quantity cannot exceed ${this.maxQuantityPerItem} per item`
        );
      }

      cartItem.quantity = newQuantity;
      await cartItem.save();
    } else {
      // Check total items limit
      const totalItems = await CartItem.count({
        where: { cart_id: cart.id },
      });

      if (totalItems >= this.maxTotalItems) {
        throw new Error(
          `Cart cannot exceed ${this.maxTotalItems} different items`
        );
      }

      // Create new cart item
      cartItem = await CartItem.create({
        cart_id: cart.id,
        product_id: productId,
        quantity,
      });
    }

    // Update cart timestamp
    cart.updated_at = new Date();
    await cart.save();

    return this.getCartWithItems(userId);
  }

  async getCartWithItems(userId) {
    const cart = await Cart.findOne({
      where: { user_id: userId },
      include: [
        {
          model: CartItem,
          as: 'items',
        },
      ],
    });

    if (!cart || !cart.items || cart.items.length === 0) {
      return null;
    }

    // Enrich cart items with product data
    const enrichedItems = await productService.enrichCartItems(cart.items);

    // Calculate totals
    const totals = this.calculateTotals(enrichedItems);

    return {
      cart_id: cart.id,
      user_id: cart.user_id,
      items: enrichedItems,
      totals,
      created_at: cart.created_at,
      updated_at: cart.updated_at,
    };
  }

  async updateItemQuantity(userId, productId, newQuantity) {
    if (newQuantity > this.maxQuantityPerItem) {
      throw new Error(
        `Quantity cannot exceed ${this.maxQuantityPerItem} per item`
      );
    }

    if (newQuantity < 1) {
      throw new Error('Quantity must be at least 1');
    }

    const cart = await this.findOrCreateCart(userId);

    const cartItem = await CartItem.findOne({
      where: {
        cart_id: cart.id,
        product_id: productId,
      },
    });

    if (!cartItem) {
      throw new Error('Item not found in cart');
    }

    cartItem.quantity = newQuantity;
    await cartItem.save();

    // Update cart timestamp
    cart.updated_at = new Date();
    await cart.save();

    return this.getCartWithItems(userId);
  }

  async removeItemFromCart(userId, productId) {
    const cart = await this.findOrCreateCart(userId);

    const cartItem = await CartItem.findOne({
      where: {
        cart_id: cart.id,
        product_id: productId,
      },
    });

    if (!cartItem) {
      throw new Error('Item not found in cart');
    }

    await cartItem.destroy();

    // Update cart timestamp
    cart.updated_at = new Date();
    await cart.save();

    return this.getCartWithItems(userId);
  }

  async clearCart(userId) {
    const cart = await this.findOrCreateCart(userId);

    // Remove all items
    await CartItem.destroy({
      where: { cart_id: cart.id },
    });

    // Update cart timestamp
    cart.updated_at = new Date();
    await cart.save();

    return {
      message: 'Cart cleared successfully',
      cart_id: cart.id,
    };
  }

  calculateTotals(enrichedItems) {
    const itemCount = enrichedItems.reduce(
      (sum, item) => sum + item.quantity,
      0
    );
    const totalPrice = enrichedItems.reduce(
      (sum, item) => sum + item.subtotal,
      0
    );

    return {
      item_count: itemCount,
      total_price: Math.round(totalPrice * 100) / 100, // Round to 2 decimal places
      currency: 'USD',
    };
  }

  async cleanupExpiredCarts() {
    const ttlHours = parseInt(process.env.CART_TTL_HOURS || '24');
    const expiredDate = new Date(Date.now() - ttlHours * 60 * 60 * 1000);

    const expiredCarts = await Cart.findAll({
      where: {
        updated_at: {
          [require('sequelize').Op.lt]: expiredDate,
        },
      },
    });

    for (const cart of expiredCarts) {
      await CartItem.destroy({
        where: { cart_id: cart.id },
      });
      await cart.destroy();
    }

    return expiredCarts.length;
  }
}

module.exports = new CartService();
