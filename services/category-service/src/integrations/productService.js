const { createServiceClient } = require('../utils/httpClient');

class ProductService {
  constructor() {
    const productServiceUrl = process.env.PRODUCT_SERVICE_URL || 'http://localhost:8004';

    this.client = createServiceClient('product-service', productServiceUrl, {
      timeout: 8000,
      retries: 3
    });

    this.cache = new Map();
    this.cacheTimeout = 180000; // 3 minutes
    this.fallbackEnabled = true;
  }

  // Get products by category ID
  async getProductsByCategory(categoryId, options = {}) {
    try {
      const {
        include_subcategories = false,
        page = 1,
        limit = 20,
        sort = 'name',
        order = 'asc'
      } = options;

      const cacheKey = `products:${categoryId}:${JSON.stringify(options)}`;
      const cached = this.cache.get(cacheKey);

      if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }

      const response = await this.client.get(`/products`, {
        params: {
          category_id: categoryId,
          include_subcategories,
          page,
          limit,
          sort,
          order
        }
      });

      const productData = {
        products: response.data.products || [],
        pagination: response.data.pagination || {
          page,
          limit,
          total: 0,
          pages: 0,
          has_next: false,
          has_prev: false
        },
        filters: response.data.filters || {}
      };

      // Cache the result
      this.cache.set(cacheKey, {
        data: productData,
        timestamp: Date.now()
      });

      return productData;
    } catch (error) {
      if (this.fallbackEnabled) {
        return this.getFallbackProductData(categoryId, options);
      }

      throw new ProductServiceError(
        `Failed to get products for category ${categoryId}: ${error.message}`,
        error.response?.status || 500,
        'PRODUCT_FETCH_FAILED'
      );
    }
  }

  // Get product count for category
  async getProductCount(categoryId, includeSubcategories = false) {
    try {
      const cacheKey = `count:${categoryId}:${includeSubcategories}`;
      const cached = this.cache.get(cacheKey);

      if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }

      const response = await this.client.get(`/products/count`, {
        params: {
          category_id: categoryId,
          include_subcategories: includeSubcategories
        }
      });

      const count = response.data.count || 0;

      // Cache the result
      this.cache.set(cacheKey, {
        data: count,
        timestamp: Date.now()
      });

      return count;
    } catch (error) {
      if (this.fallbackEnabled) {
        // Return mock count for graceful degradation
        return Math.floor(Math.random() * 50);
      }

      throw new ProductServiceError(
        `Failed to get product count for category ${categoryId}: ${error.message}`,
        error.response?.status || 500,
        'PRODUCT_COUNT_FAILED'
      );
    }
  }

  // Get product counts for multiple categories
  async getProductCounts(categoryIds, includeSubcategories = false) {
    try {
      const cacheKey = `counts:${categoryIds.join(',')}:${includeSubcategories}`;
      const cached = this.cache.get(cacheKey);

      if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }

      const response = await this.client.post('/products/counts', {
        category_ids: categoryIds,
        include_subcategories: includeSubcategories
      });

      const counts = response.data.counts || {};

      // Cache the result
      this.cache.set(cacheKey, {
        data: counts,
        timestamp: Date.now()
      });

      return counts;
    } catch (error) {
      if (this.fallbackEnabled) {
        // Return mock counts for graceful degradation
        const mockCounts = {};
        categoryIds.forEach(id => {
          mockCounts[id] = Math.floor(Math.random() * 50);
        });
        return mockCounts;
      }

      throw new ProductServiceError(
        `Failed to get product counts for categories: ${error.message}`,
        error.response?.status || 500,
        'PRODUCT_COUNTS_FAILED'
      );
    }
  }

  // Notify product service about category changes
  async notifyCategoryChange(action, categoryData) {
    try {
      const payload = {
        action, // 'created', 'updated', 'deleted'
        category: categoryData,
        timestamp: new Date().toISOString()
      };

      await this.client.post('/categories/notifications', payload);

      return { success: true };
    } catch (error) {
      console.error('Failed to notify product service about category change:', error.message);
      // Don't throw error for notifications to avoid blocking category operations
      return { success: false, error: error.message };
    }
  }

  // Update product category associations
  async updateProductCategories(productId, categoryIds) {
    try {
      const response = await this.client.put(`/products/${productId}/categories`, {
        category_ids: categoryIds
      });

      return response.data;
    } catch (error) {
      throw new ProductServiceError(
        `Failed to update product categories: ${error.message}`,
        error.response?.status || 500,
        'PRODUCT_CATEGORY_UPDATE_FAILED'
      );
    }
  }

  // Search products within categories
  async searchProducts(query, categoryIds = [], options = {}) {
    try {
      const {
        page = 1,
        limit = 20,
        sort = 'relevance',
        order = 'desc'
      } = options;

      const response = await this.client.get('/products/search', {
        params: {
          q: query,
          category_ids: categoryIds.join(','),
          page,
          limit,
          sort,
          order
        }
      });

      return {
        products: response.data.products || [],
        pagination: response.data.pagination || {},
        query,
        filters: response.data.filters || {}
      };
    } catch (error) {
      if (this.fallbackEnabled) {
        return {
          products: [],
          pagination: { page, limit, total: 0, pages: 0 },
          query,
          filters: {}
        };
      }

      throw new ProductServiceError(
        `Product search failed: ${error.message}`,
        error.response?.status || 500,
        'PRODUCT_SEARCH_FAILED'
      );
    }
  }

  // Health check for product service
  async checkHealth() {
    try {
      return await this.client.checkHealth();
    } catch (error) {
      return {
        status: 'unhealthy',
        service: 'product-service',
        error: error.message
      };
    }
  }

  // Get service status including circuit breaker
  getServiceStatus() {
    const circuitStatus = this.client.getCircuitStatus();

    return {
      serviceName: 'product-service',
      baseURL: this.client.baseURL,
      circuit: circuitStatus,
      cache: {
        size: this.cache.size,
        timeout: this.cacheTimeout
      },
      fallback: {
        enabled: this.fallbackEnabled
      }
    };
  }

  // Fallback data for graceful degradation
  getFallbackProductData(categoryId, options = {}) {
    const { page = 1, limit = 20 } = options;

    console.warn(`Using fallback data for category ${categoryId} products`);

    return {
      products: [], // Empty products list
      pagination: {
        page,
        limit,
        total: 0,
        pages: 0,
        has_next: false,
        has_prev: false
      },
      filters: {},
      fallback: true,
      message: 'Product catalog service unavailable - showing cached or default data'
    };
  }

  // Enable/disable fallback mode
  setFallbackMode(enabled) {
    this.fallbackEnabled = enabled;
  }

  // Clear cache
  clearCache() {
    this.cache.clear();
  }

  // Clear expired cache entries
  clearExpiredCache() {
    const now = Date.now();
    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp >= this.cacheTimeout) {
        this.cache.delete(key);
      }
    }
  }

  // Preload product counts for categories
  async preloadProductCounts(categoryIds) {
    try {
      const chunks = [];
      const chunkSize = 10; // Process in chunks to avoid overwhelming the service

      for (let i = 0; i < categoryIds.length; i += chunkSize) {
        chunks.push(categoryIds.slice(i, i + chunkSize));
      }

      const results = [];
      for (const chunk of chunks) {
        try {
          const counts = await this.getProductCounts(chunk);
          results.push(counts);
        } catch (error) {
          console.error('Failed to preload product counts for chunk:', error.message);
        }
      }

      return results.reduce((acc, counts) => ({ ...acc, ...counts }), {});
    } catch (error) {
      console.error('Failed to preload product counts:', error.message);
      return {};
    }
  }

  // Validate category-product relationship
  async validateCategoryProducts(categoryId) {
    try {
      const response = await this.client.get(`/categories/${categoryId}/validate`);
      return response.data;
    } catch (error) {
      console.error('Category product validation failed:', error.message);
      return { valid: false, error: error.message };
    }
  }

  // Start cache cleanup interval
  startCacheCleanup(intervalMs = 180000) { // 3 minutes
    setInterval(() => {
      this.clearExpiredCache();
    }, intervalMs);
  }
}

// Custom error class for product service errors
class ProductServiceError extends Error {
  constructor(message, statusCode = 500, code = 'PRODUCT_SERVICE_ERROR') {
    super(message);
    this.name = 'ProductServiceError';
    this.statusCode = statusCode;
    this.code = code;
  }
}

// Singleton instance
let productServiceInstance = null;

function getProductService() {
  if (!productServiceInstance) {
    productServiceInstance = new ProductService();
    productServiceInstance.startCacheCleanup();
  }
  return productServiceInstance;
}

module.exports = {
  ProductService,
  ProductServiceError,
  getProductService
};