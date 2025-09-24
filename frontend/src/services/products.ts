/**
 * Products service client
 * Handles all product catalog API calls
 */

import { productsApi, handleApiCall, buildQueryParams } from '@/lib/api';
import { Product, ProductsResponse, ProductFilters, Category, CategoriesResponse, RelatedProductsResponse, ProductSearchResponse, ProductDetailResponse } from '@/types/product';
import { productCache, cacheKeys, cacheTTL, persistentCache } from '@/lib/cache';

export class ProductsService {
  /**
   * Get list of products with optional filtering and pagination
   */
  static async getProducts(filters?: ProductFilters): Promise<ProductsResponse> {
    const cacheKey = cacheKeys.products(filters);

    // Try to get from cache first
    const cachedData = productCache.get<ProductsResponse>(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    // Try persistent cache for offline support
    const persistentData = persistentCache.get<ProductsResponse>(cacheKey);
    if (persistentData) {
      // Refresh cache in background
      productCache.set(cacheKey, persistentData, cacheTTL.products);
      return persistentData;
    }

    const queryParams = filters ? `?${buildQueryParams(filters)}` : '';

    const response = await handleApiCall(
      () => productsApi.get<ProductsResponse>(`/products${queryParams}`),
      'get products'
    );

    // Cache the response
    productCache.set(cacheKey, response, cacheTTL.products);
    persistentCache.set(cacheKey, response, cacheTTL.products);

    return response;
  }

  /**
   * Get detailed information for a specific product
   */
  static async getProduct(id: string): Promise<Product> {
    const cacheKey = cacheKeys.product(id);

    // Try to get from cache first
    const cachedData = productCache.get<Product>(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    // Try persistent cache for offline support
    const persistentData = persistentCache.get<Product>(cacheKey);
    if (persistentData) {
      // Refresh cache in background
      productCache.set(cacheKey, persistentData, cacheTTL.product);
      return persistentData;
    }

    const response = await handleApiCall(
      () => productsApi.get<ProductDetailResponse>(`/products/${id}`),
      `get product ${id}`
    );

    // Transform API response
    const product = this.transformProductFromApi(response);

    // Cache the response
    productCache.set(cacheKey, product, cacheTTL.product);
    persistentCache.set(cacheKey, product, cacheTTL.product);

    return product;
  }

  /**
   * Get list of product categories
   */
  static async getCategories(): Promise<CategoriesResponse> {
    const cacheKey = cacheKeys.categories();

    // Try to get from cache first
    const cachedData = productCache.get<CategoriesResponse>(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    // Try persistent cache for offline support
    const persistentData = persistentCache.get<CategoriesResponse>(cacheKey);
    if (persistentData) {
      // Refresh cache in background
      productCache.set(cacheKey, persistentData, cacheTTL.categories);
      return persistentData;
    }

    const response = await handleApiCall(
      () => productsApi.get<CategoriesResponse>('/categories'),
      'get categories'
    );

    // Cache the response
    productCache.set(cacheKey, response, cacheTTL.categories);
    persistentCache.set(cacheKey, response, cacheTTL.categories);

    return response;
  }

  /**
   * Get related products for a specific product
   */
  static async getRelatedProducts(id: string, limit: number = 4): Promise<RelatedProductsResponse> {
    return handleApiCall(
      () => productsApi.get<RelatedProductsResponse>(`/products/${id}/related?limit=${limit}`),
      `get related products for ${id}`
    );
  }

  /**
   * Advanced product search with faceted filtering
   */
  static async searchProducts(query: string, filters?: Partial<ProductFilters>): Promise<ProductSearchResponse> {
    const cacheKey = cacheKeys.searchResults(query, filters);

    // Try to get from cache first
    const cachedData = productCache.get<ProductSearchResponse>(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    const params = {
      q: query,
      ...filters,
    };

    const queryParams = `?${buildQueryParams(params)}`;

    const response = await handleApiCall(
      () => productsApi.get<ProductSearchResponse>(`/products/search${queryParams}`),
      `search products: ${query}`
    );

    // Cache the response with shorter TTL for search results
    productCache.set(cacheKey, response, cacheTTL.search);

    return response;
  }

  /**
   * Format price from cents to display format
   */
  static formatPrice(priceInCents: number, currency: string = 'USD'): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(priceInCents / 100);
  }

  /**
   * Check if product is available for purchase
   */
  static isProductAvailable(product: Product): boolean {
    return product.inStock && product.stockQuantity > 0;
  }

  /**
   * Get product availability status text
   */
  static getAvailabilityText(product: Product): string {
    if (!product.inStock) {
      return 'Out of stock';
    }

    if (product.stockQuantity <= 5) {
      return `Only ${product.stockQuantity} left`;
    }

    return 'In stock';
  }

  /**
   * Get product availability status type
   */
  static getAvailabilityStatus(product: Product): 'available' | 'low-stock' | 'out-of-stock' {
    if (!product.inStock || product.stockQuantity === 0) {
      return 'out-of-stock';
    }

    if (product.stockQuantity <= 5) {
      return 'low-stock';
    }

    return 'available';
  }

  /**
   * Filter products by category
   */
  static filterByCategory(products: Product[], categorySlug: string): Product[] {
    return products.filter(product => product.category === categorySlug);
  }

  /**
   * Filter products by price range
   */
  static filterByPriceRange(products: Product[], minPrice: number, maxPrice: number): Product[] {
    return products.filter(product =>
      product.price >= minPrice && product.price <= maxPrice
    );
  }

  /**
   * Filter products by availability
   */
  static filterByAvailability(products: Product[], inStock: boolean): Product[] {
    return products.filter(product => product.inStock === inStock);
  }

  /**
   * Sort products by specified field and order
   */
  static sortProducts(
    products: Product[],
    sortBy: 'name' | 'price' | 'created_at' = 'name',
    order: 'asc' | 'desc' = 'asc'
  ): Product[] {
    return [...products].sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'price':
          comparison = a.price - b.price;
          break;
        case 'created_at':
          comparison = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
          break;
      }

      return order === 'desc' ? -comparison : comparison;
    });
  }

  /**
   * Search products by name or description
   */
  static searchProductsLocally(products: Product[], query: string): Product[] {
    const searchTerm = query.toLowerCase().trim();

    return products.filter(product =>
      product.name.toLowerCase().includes(searchTerm) ||
      product.description.toLowerCase().includes(searchTerm)
    );
  }

  /**
   * Get unique categories from products list
   */
  static getUniqueCategories(products: Product[]): string[] {
    const categories = products.map(product => product.category);
    return Array.from(new Set(categories)).sort();
  }

  /**
   * Get price range from products list
   */
  static getPriceRange(products: Product[]): { min: number; max: number } {
    if (products.length === 0) {
      return { min: 0, max: 0 };
    }

    const prices = products.map(product => product.price);
    return {
      min: Math.min(...prices),
      max: Math.max(...prices),
    };
  }

  /**
   * Build breadcrumb from category hierarchy
   */
  static buildCategoryBreadcrumb(categories: Category[], currentCategorySlug: string): Category[] {
    const breadcrumb: Category[] = [];
    let current = categories.find(cat => cat.slug === currentCategorySlug);

    while (current) {
      breadcrumb.unshift(current);
      current = current.parentId ? categories.find(cat => cat.id === current!.parentId) : undefined;
    }

    return breadcrumb;
  }

  /**
   * Transform API response to match frontend interface
   */
  static transformProductFromApi(
    apiProduct: ProductDetailResponse | ProductsResponse['products'][number]
  ): Product {
    return {
      id: apiProduct.id,
      name: apiProduct.name,
      description: apiProduct.description,
      price: apiProduct.price,
      currency: apiProduct.currency,
      category: apiProduct.category,
      imageUrl: apiProduct.image_url,
      images: apiProduct.images || [apiProduct.image_url],
      inStock: apiProduct.in_stock,
      stockQuantity: apiProduct.stock_quantity,
      specifications: apiProduct.specifications || {},
      createdAt: apiProduct.created_at,
      updatedAt: apiProduct.updated_at,
    };
  }
}

export default ProductsService;
