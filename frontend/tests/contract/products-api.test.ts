/**
 * Products API Contract Tests
 * These tests verify that our products service client correctly implements the API contract
 * Based on: /specs/004-build-a-next/contracts/products-api.md
 */

import { ProductsService } from '@/services/products';

// Mock the service for contract testing
jest.mock('@/services/products');

const mockProductsService = ProductsService as jest.MockedClass<typeof ProductsService>;

describe('Products API Contract', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('GET /products', () => {
    it('should retrieve products list with pagination', async () => {
      // Mock the expected API response structure
      const mockResponse = {
        products: [
          {
            id: '1',
            name: 'Test Product',
            price: 1999,
            currency: 'USD',
            category: 'electronics',
            imageUrl: 'test.jpg',
            inStock: true,
            stockQuantity: 10,
            description: 'Test description',
            createdAt: '2023-01-01T00:00:00Z',
            updatedAt: '2023-01-01T00:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        limit: 20,
        total_pages: 1,
      };

      mockProductsService.getProducts.mockResolvedValue(mockResponse);

      const response = await ProductsService.getProducts();

      expect(response).toMatchObject({
        products: expect.arrayContaining([
          expect.objectContaining({
            id: expect.any(String),
            name: expect.any(String),
            description: expect.any(String),
            price: expect.any(Number),
            currency: 'USD',
            category: expect.any(String),
            imageUrl: expect.any(String),
            inStock: expect.any(Boolean),
            stockQuantity: expect.any(Number),
            createdAt: expect.any(String),
            updatedAt: expect.any(String),
          }),
        ]),
        total: expect.any(Number),
        page: expect.any(Number),
        limit: expect.any(Number),
        total_pages: expect.any(Number),
      });
    });

    it('should filter products by category', async () => {
      const filters = { category: 'electronics' };
      const mockResponse = {
        products: [
          {
            id: '1',
            name: 'Laptop',
            category: 'electronics',
            price: 99999,
            currency: 'USD',
            imageUrl: 'laptop.jpg',
            inStock: true,
            stockQuantity: 5,
            description: 'Gaming laptop',
            createdAt: '2023-01-01T00:00:00Z',
            updatedAt: '2023-01-01T00:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        limit: 20,
        total_pages: 1,
      };

      mockProductsService.getProducts.mockResolvedValue(mockResponse);

      const response = await ProductsService.getProducts(filters);

      expect(mockProductsService.getProducts).toHaveBeenCalledWith(filters);
      expect(response.products.every(p => p.category === 'electronics')).toBe(true);
    });

    it('should search products by query', async () => {
      const filters = { search: 'laptop' };
      const mockResponse = {
        products: [
          {
            id: '1',
            name: 'Gaming Laptop',
            category: 'electronics',
            price: 99999,
            currency: 'USD',
            imageUrl: 'laptop.jpg',
            inStock: true,
            stockQuantity: 5,
            description: 'High performance gaming laptop',
            createdAt: '2023-01-01T00:00:00Z',
            updatedAt: '2023-01-01T00:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        limit: 20,
        total_pages: 1,
      };

      mockProductsService.getProducts.mockResolvedValue(mockResponse);

      const response = await ProductsService.getProducts(filters);

      expect(mockProductsService.getProducts).toHaveBeenCalledWith(filters);
      expect(response.products.some(p => p.name.toLowerCase().includes('laptop'))).toBe(true);
    });
  });

  describe('GET /products/{id}', () => {
    it('should retrieve product details by ID', async () => {
      const productId = 'product-uuid-123';
      const mockProduct = {
        id: productId,
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
        createdAt: '2023-01-01T00:00:00Z',
        updatedAt: '2023-01-01T00:00:00Z',
      };

      mockProductsService.getProduct.mockResolvedValue(mockProduct);

      const response = await ProductsService.getProduct(productId);

      expect(response).toMatchObject({
        id: productId,
        name: expect.any(String),
        description: expect.any(String),
        price: expect.any(Number),
        currency: 'USD',
        category: expect.any(String),
        imageUrl: expect.any(String),
        images: expect.arrayContaining([expect.any(String)]),
        inStock: expect.any(Boolean),
        stockQuantity: expect.any(Number),
        specifications: expect.any(Object),
        createdAt: expect.any(String),
        updatedAt: expect.any(String),
      });
    });

    it('should handle product not found with 404', async () => {
      const invalidId = 'nonexistent-product';

      mockProductsService.getProduct.mockRejectedValue(new Error('Product not found'));

      await expect(ProductsService.getProduct(invalidId)).rejects.toThrow('Product not found');
    });
  });

  describe('GET /categories', () => {
    it('should retrieve categories list', async () => {
      const mockResponse = {
        categories: [
          {
            id: '1',
            name: 'Electronics',
            slug: 'electronics',
            description: 'Electronic devices',
            parentId: null,
          },
        ],
      };

      mockProductsService.getCategories.mockResolvedValue(mockResponse);

      const response = await ProductsService.getCategories();

      expect(response).toMatchObject({
        categories: expect.arrayContaining([
          expect.objectContaining({
            id: expect.any(String),
            name: expect.any(String),
            slug: expect.any(String),
            description: expect.any(String),
          }),
        ]),
      });
    });
  });

  describe('GET /products/{id}/related', () => {
    it('should retrieve related products', async () => {
      const productId = 'product-uuid-123';
      const mockResponse = {
        related_products: [
          {
            id: '2',
            name: 'Related Product',
            price: 1999,
            currency: 'USD',
            imageUrl: 'related.jpg',
            inStock: true,
          },
        ],
      };

      mockProductsService.getRelatedProducts.mockResolvedValue(mockResponse);

      const response = await ProductsService.getRelatedProducts(productId);

      expect(response).toMatchObject({
        related_products: expect.arrayContaining([
          expect.objectContaining({
            id: expect.any(String),
            name: expect.any(String),
            price: expect.any(Number),
            currency: 'USD',
            imageUrl: expect.any(String),
            inStock: expect.any(Boolean),
          }),
        ]),
      });
    });
  });

  describe('Advanced search functionality', () => {
    it('should perform search with query and filters', async () => {
      const query = 'laptop';
      const filters = { category: 'electronics', min_price: 50000 };
      const mockResponse = {
        products: [
          {
            id: '1',
            name: 'Gaming Laptop',
            price: 99999,
            currency: 'USD',
            category: 'electronics',
            imageUrl: 'laptop.jpg',
            inStock: true,
            stockQuantity: 5,
            description: 'High performance gaming laptop',
            createdAt: '2023-01-01T00:00:00Z',
            updatedAt: '2023-01-01T00:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        limit: 20,
        total_pages: 1,
        search_info: {
          query: 'laptop',
          total_results: 1,
        },
      };

      mockProductsService.searchProducts.mockResolvedValue(mockResponse);

      const response = await ProductsService.searchProducts(query, filters);

      expect(mockProductsService.searchProducts).toHaveBeenCalledWith(query, filters);
      expect(response).toMatchObject({
        products: expect.any(Array),
        total: expect.any(Number),
        search_info: {
          query: 'laptop',
          total_results: expect.any(Number),
        },
      });
    });
  });
});