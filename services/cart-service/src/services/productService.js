const axios = require('axios');

class ProductService {
  constructor() {
    this.productServiceUrl =
      process.env.PRODUCT_SERVICE_URL || 'http://localhost:8002';
    this.timeout = parseInt(process.env.REQUEST_TIMEOUT || '5000');
  }

  async getProduct(productId) {
    try {
      const response = await axios.get(
        `${this.productServiceUrl}/products/${productId}`,
        {
          timeout: this.timeout,
        }
      );

      if (response.status === 200) {
        return response.data;
      }

      return null;
    } catch (error) {
      if (error.response?.status === 404) {
        return null;
      }

      if (error.code === 'ECONNREFUSED' || error.code === 'TIMEOUT') {
        throw new Error('Product service unavailable');
      }

      throw new Error(`Product service error: ${error.message}`);
    }
  }

  async validateProducts(productIds) {
    try {
      const response = await axios.post(
        `${this.productServiceUrl}/products/validate`,
        {
          product_ids: productIds,
        },
        {
          timeout: this.timeout,
        }
      );

      if (response.status === 200) {
        return response.data.products || [];
      }

      return [];
    } catch (error) {
      if (error.code === 'ECONNREFUSED' || error.code === 'TIMEOUT') {
        throw new Error('Product service unavailable');
      }

      throw new Error(`Product validation error: ${error.message}`);
    }
  }

  async enrichCartItems(cartItems) {
    if (!cartItems || cartItems.length === 0) {
      return [];
    }

    try {
      // Extract unique product IDs
      const productIds = [...new Set(cartItems.map((item) => item.product_id))];

      // Get product details for all items
      const productPromises = productIds.map((id) => this.getProduct(id));
      const products = await Promise.all(productPromises);

      // Create product lookup map
      const productMap = {};
      products.forEach((product, index) => {
        if (product) {
          productMap[productIds[index]] = product;
        }
      });

      // Enrich cart items with product data
      return cartItems.map((item) => {
        const product = productMap[item.product_id];
        if (!product) {
          throw new Error(`Product ${item.product_id} not found`);
        }

        const subtotal = product.price * item.quantity;

        return {
          product_id: item.product_id,
          quantity: item.quantity,
          product: {
            id: product.id,
            name: product.name,
            price: product.price,
            description: product.description || '',
            image_url: product.image_url || '',
            availability: product.availability !== false,
          },
          subtotal: Math.round(subtotal * 100) / 100, // Round to 2 decimal places
          added_at: item.created_at,
        };
      });
    } catch (error) {
      throw new Error(`Failed to enrich cart items: ${error.message}`);
    }
  }

  async checkHealth() {
    try {
      const response = await axios.get(`${this.productServiceUrl}/health`, {
        timeout: this.timeout,
      });
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }

  async isProductAvailable(productId) {
    try {
      const product = await this.getProduct(productId);
      return product && product.availability !== false;
    } catch (error) {
      return false;
    }
  }
}

module.exports = new ProductService();
