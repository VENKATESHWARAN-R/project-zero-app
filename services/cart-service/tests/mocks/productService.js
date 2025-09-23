// Mock product service for testing
const mockProductService = {
  products: new Map(),

  // Set up default mock products
  init: () => {
    const defaultProducts = {
      'prod-123': { id: 'prod-123', name: 'Sample Product', price: 29.99, description: 'A great product', availability: true },
      'prod-laptop-123': { id: 'prod-laptop-123', name: 'Gaming Laptop', price: 1299.99, description: 'High-performance gaming laptop', availability: true },
      'prod-mouse-456': { id: 'prod-mouse-456', name: 'Wireless Mouse', price: 49.99, description: 'Ergonomic wireless mouse', availability: true },
      'prod-keyboard-789': { id: 'prod-keyboard-789', name: 'Mechanical Keyboard', price: 149.99, description: 'RGB mechanical keyboard', availability: true },
      'prod-monitor-999': { id: 'prod-monitor-999', name: '4K Monitor', price: 399.99, description: '27-inch 4K monitor', availability: true },
      'prod-book-100': { id: 'prod-book-100', name: 'Programming Book', price: 10.00, description: 'Learn to code', availability: true },
      'prod-valid-12345': { id: 'prod-valid-12345', name: 'Valid Product', price: 19.99, description: 'A valid test product', availability: true },
      'prod-enrichment-test': { id: 'prod-enrichment-test', name: 'Enrichment Test Product', price: 25.50, description: 'Product for enrichment testing', image_url: 'https://example.com/image.jpg', availability: true },
      'prod-get-validation': { id: 'prod-get-validation', name: 'Get Validation Product', price: 15.75, description: 'Product for get validation', availability: true },
      'prod-bulk-1': { id: 'prod-bulk-1', name: 'Bulk Product 1', price: 12.99, description: 'Bulk test product 1', availability: true },
      'prod-bulk-2': { id: 'prod-bulk-2', name: 'Bulk Product 2', price: 22.99, description: 'Bulk test product 2', availability: true },
      'prod-bulk-3': { id: 'prod-bulk-3', name: 'Bulk Product 3', price: 32.99, description: 'Bulk test product 3', availability: true },
      'prod-price-change': { id: 'prod-price-change', name: 'Price Change Product', price: 50.00, description: 'Product with changing price', availability: true },
      'prod-persistence-test': { id: 'prod-persistence-test', name: 'Persistence Test Product', price: 75.00, description: 'Product for persistence testing', availability: true },
      'prod-state-1': { id: 'prod-state-1', name: 'State Test Product 1', price: 10.00, description: 'State test product 1', availability: true },
      'prod-state-2': { id: 'prod-state-2', name: 'State Test Product 2', price: 20.00, description: 'State test product 2', availability: true },
      'prod-state-3': { id: 'prod-state-3', name: 'State Test Product 3', price: 30.00, description: 'State test product 3', availability: true },
      'prod-expiry-test': { id: 'prod-expiry-test', name: 'Expiry Test Product', price: 5.00, description: 'Product for expiry testing', availability: true },
      'prod-concurrent-1': { id: 'prod-concurrent-1', name: 'Concurrent Product 1', price: 8.00, description: 'Concurrent test product 1', availability: true },
      'prod-concurrent-2': { id: 'prod-concurrent-2', name: 'Concurrent Product 2', price: 16.00, description: 'Concurrent test product 2', availability: true },
      'prod-concurrent-3': { id: 'prod-concurrent-3', name: 'Concurrent Product 3', price: 24.00, description: 'Concurrent test product 3', availability: true },
      'prod-timestamp-test': { id: 'prod-timestamp-test', name: 'Timestamp Test Product', price: 99.99, description: 'Product for timestamp testing', availability: true },
      'prod-discontinued-999': { id: 'prod-discontinued-999', name: 'Discontinued Product', price: 199.99, description: 'Not available product', availability: false },
    };

    Object.entries(defaultProducts).forEach(([id, product]) => {
      mockProductService.products.set(id, product);
    });
  },

  // Add or update a mock product
  setProduct: (productId, product) => {
    mockProductService.products.set(productId, product);
  },

  // Remove a mock product
  removeProduct: (productId) => {
    mockProductService.products.delete(productId);
  },

  // Clear all products
  clearProducts: () => {
    mockProductService.products.clear();
  },

  // Mock implementation
  async getProduct(productId) {
    if (productId === 'prod-does-not-exist') {
      return null;
    }

    if (productId === 'prod-service-error') {
      throw new Error('Product service unavailable');
    }

    return mockProductService.products.get(productId) || null;
  },

  async validateProducts(productIds) {
    const products = [];
    for (const id of productIds) {
      const product = await mockProductService.getProduct(id);
      if (product) {
        products.push(product);
      }
    }
    return products;
  },

  async enrichCartItems(cartItems) {
    if (!cartItems || cartItems.length === 0) {
      return [];
    }

    const enrichedItems = [];
    for (const item of cartItems) {
      const product = await mockProductService.getProduct(item.product_id);
      if (!product) {
        throw new Error(`Product ${item.product_id} not found`);
      }

      const subtotal = product.price * item.quantity;

      enrichedItems.push({
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
        subtotal: Math.round(subtotal * 100) / 100,
        added_at: item.created_at,
      });
    }

    return enrichedItems;
  },

  async checkHealth() {
    return true;
  },

  async isProductAvailable(productId) {
    const product = await mockProductService.getProduct(productId);
    return product && product.availability !== false;
  },
};

// Initialize default products
mockProductService.init();

module.exports = mockProductService;