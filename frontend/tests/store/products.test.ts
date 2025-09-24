/**
 * Products Store Tests
 * Tests for the products management Zustand store
 */

import { act, renderHook } from '@testing-library/react';
import { useProductStore } from '@/store/products';
import { ProductsService } from '@/services/products';

// Mock the products service
jest.mock('@/services/products');

const mockProductsService = ProductsService as jest.MockedClass<typeof ProductsService>;

const mockProduct = {
  id: 'product-1',
  name: 'Gaming Laptop Pro',
  description: 'High-performance gaming laptop',
  price: 149999,
  currency: 'USD',
  category: 'electronics',
  image_url: 'https://example.com/laptop.jpg',
  in_stock: true,
  stock_quantity: 15,
  created_at: '2025-09-24T10:00:00Z',
  updated_at: '2025-09-24T10:00:00Z',
};

const mockProductsResponse = {
  products: [mockProduct],
  pagination: {
    page: 1,
    limit: 20,
    total: 1,
    total_pages: 1,
    has_next: false,
    has_prev: false,
  },
  filters_applied: {},
};

const mockCategories = {
  categories: [
    {
      id: 'cat-1',
      name: 'Electronics',
      slug: 'electronics',
      description: 'Electronic devices',
      parent_id: null,
      product_count: 25,
    },
  ],
};

const mockDetailedProduct = {
  ...mockProduct,
  images: [
    'https://example.com/laptop-1.jpg',
    'https://example.com/laptop-2.jpg',
  ],
  specifications: {
    cpu: 'Intel Core i9-13900H',
    gpu: 'NVIDIA RTX 4080',
    ram: '32GB DDR5',
    storage: '1TB NVMe SSD',
  },
};

describe('Products Store', () => {
  beforeEach(() => {
    // Reset store state
    useProductStore.setState({
      products: [],
      categories: [],
      currentProduct: null,
      isLoading: false,
      error: null,
      filters: {
        category: null,
        search: '',
        priceRange: null,
      },
    });

    // Reset mocks
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useProductStore());

      expect(result.current.products).toEqual([]);
      expect(result.current.categories).toEqual([]);
      expect(result.current.currentProduct).toBeNull();
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.filters).toEqual({
        category: null,
        search: '',
        priceRange: null,
      });
    });
  });

  describe('Load Products', () => {
    it('should load products successfully', async () => {
      const mockGetProducts = jest.fn().mockResolvedValue(mockProductsResponse);
      mockProductsService.prototype.getProducts = mockGetProducts;

      const { result } = renderHook(() => useProductStore());

      await act(async () => {
        await result.current.loadProducts();
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.products).toEqual([
        {
          id: 'product-1',
          name: 'Gaming Laptop Pro',
          description: 'High-performance gaming laptop',
          price: 149999,
          currency: 'USD',
          category: 'electronics',
          imageUrl: 'https://example.com/laptop.jpg',
          inStock: true,
          stockQuantity: 15,
          createdAt: '2025-09-24T10:00:00Z',
          updatedAt: '2025-09-24T10:00:00Z',
        },
      ]);
      expect(result.current.error).toBeNull();
    });

    it('should load products with filters', async () => {
      const mockGetProducts = jest.fn().mockResolvedValue(mockProductsResponse);
      mockProductsService.prototype.getProducts = mockGetProducts;

      const { result } = renderHook(() => useProductStore());

      const filters = { category: 'electronics', search: 'laptop' };

      await act(async () => {
        await result.current.loadProducts(filters);
      });

      expect(mockGetProducts).toHaveBeenCalledWith(filters);
    });

    it('should handle load products failure', async () => {
      const mockGetProducts = jest.fn().mockRejectedValue(new Error('Failed to load products'));
      mockProductsService.prototype.getProducts = mockGetProducts;

      const { result } = renderHook(() => useProductStore());

      await act(async () => {
        await result.current.loadProducts();
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.products).toEqual([]);
      expect(result.current.error).toBe('Failed to load products');
    });

    it('should set loading state during products load', async () => {
      const mockGetProducts = jest.fn().mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockProductsResponse), 100))
      );
      mockProductsService.prototype.getProducts = mockGetProducts;

      const { result } = renderHook(() => useProductStore());

      act(() => {
        result.current.loadProducts();
      });

      expect(result.current.isLoading).toBe(true);

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 150));
      });

      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('Load Single Product', () => {
    it('should load product details successfully', async () => {
      const mockGetProduct = jest.fn().mockResolvedValue(mockDetailedProduct);
      mockProductsService.prototype.getProduct = mockGetProduct;

      const { result } = renderHook(() => useProductStore());

      await act(async () => {
        await result.current.loadProduct('product-1');
      });

      expect(result.current.currentProduct).toEqual({
        id: 'product-1',
        name: 'Gaming Laptop Pro',
        description: 'High-performance gaming laptop',
        price: 149999,
        currency: 'USD',
        category: 'electronics',
        imageUrl: 'https://example.com/laptop.jpg',
        images: [
          'https://example.com/laptop-1.jpg',
          'https://example.com/laptop-2.jpg',
        ],
        inStock: true,
        stockQuantity: 15,
        specifications: {
          cpu: 'Intel Core i9-13900H',
          gpu: 'NVIDIA RTX 4080',
          ram: '32GB DDR5',
          storage: '1TB NVMe SSD',
        },
        createdAt: '2025-09-24T10:00:00Z',
        updatedAt: '2025-09-24T10:00:00Z',
      });
      expect(mockGetProduct).toHaveBeenCalledWith('product-1');
    });

    it('should handle product not found', async () => {
      const mockGetProduct = jest.fn().mockRejectedValue(new Error('Product not found'));
      mockProductsService.prototype.getProduct = mockGetProduct;

      const { result } = renderHook(() => useProductStore());

      await act(async () => {
        await result.current.loadProduct('invalid-id');
      });

      expect(result.current.currentProduct).toBeNull();
      expect(result.current.error).toBe('Product not found');
    });
  });

  describe('Load Categories', () => {
    it('should load categories successfully', async () => {
      const mockGetCategories = jest.fn().mockResolvedValue(mockCategories);
      mockProductsService.prototype.getCategories = mockGetCategories;

      const { result } = renderHook(() => useProductStore());

      await act(async () => {
        await result.current.loadCategories();
      });

      expect(result.current.categories).toEqual([
        {
          id: 'cat-1',
          name: 'Electronics',
          slug: 'electronics',
          description: 'Electronic devices',
          parentId: null,
          productCount: 25,
        },
      ]);
    });

    it('should handle load categories failure', async () => {
      const mockGetCategories = jest.fn().mockRejectedValue(new Error('Failed to load categories'));
      mockProductsService.prototype.getCategories = mockGetCategories;

      const { result } = renderHook(() => useProductStore());

      await act(async () => {
        await result.current.loadCategories();
      });

      expect(result.current.categories).toEqual([]);
      expect(result.current.error).toBe('Failed to load categories');
    });
  });

  describe('Filters Management', () => {
    it('should set filters and reload products', async () => {
      const mockGetProducts = jest.fn().mockResolvedValue(mockProductsResponse);
      mockProductsService.prototype.getProducts = mockGetProducts;

      const { result } = renderHook(() => useProductStore());

      const newFilters = {
        category: 'electronics',
        search: 'laptop',
        priceRange: [50000, 200000] as [number, number],
      };

      await act(async () => {
        await result.current.setFilters(newFilters);
      });

      expect(result.current.filters).toEqual({
        category: 'electronics',
        search: 'laptop',
        priceRange: [50000, 200000],
      });
      expect(mockGetProducts).toHaveBeenCalledWith(newFilters);
    });

    it('should partially update filters', async () => {
      const mockGetProducts = jest.fn().mockResolvedValue(mockProductsResponse);
      mockProductsService.prototype.getProducts = mockGetProducts;

      const { result } = renderHook(() => useProductStore());

      // Set initial filters
      act(() => {
        useProductStore.setState({
          filters: {
            category: 'electronics',
            search: 'laptop',
            priceRange: null,
          },
        });
      });

      await act(async () => {
        await result.current.setFilters({ search: 'gaming' });
      });

      expect(result.current.filters).toEqual({
        category: 'electronics',
        search: 'gaming',
        priceRange: null,
      });
    });

    it('should clear filters', async () => {
      const mockGetProducts = jest.fn().mockResolvedValue(mockProductsResponse);
      mockProductsService.prototype.getProducts = mockGetProducts;

      const { result } = renderHook(() => useProductStore());

      // Set initial filters
      act(() => {
        useProductStore.setState({
          filters: {
            category: 'electronics',
            search: 'laptop',
            priceRange: [50000, 200000],
          },
        });
      });

      await act(async () => {
        await result.current.clearFilters();
      });

      expect(result.current.filters).toEqual({
        category: null,
        search: '',
        priceRange: null,
      });
      expect(mockGetProducts).toHaveBeenCalledWith({
        category: null,
        search: '',
        priceRange: null,
      });
    });
  });

  describe('Error Handling', () => {
    it('should clear error', () => {
      const { result } = renderHook(() => useProductStore());

      act(() => {
        useProductStore.setState({ error: 'Some error' });
      });

      expect(result.current.error).toBe('Some error');

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('Search Products', () => {
    it('should search products with advanced filters', async () => {
      const mockSearchProducts = jest.fn().mockResolvedValue({
        products: [mockProduct],
        facets: {
          categories: [{ slug: 'electronics', name: 'Electronics', count: 15 }],
          brands: [{ name: 'Dell', count: 5 }],
          price_ranges: [{ min: 50000, max: 100000, count: 8 }],
        },
        pagination: mockProductsResponse.pagination,
        search_info: {
          query: 'laptop',
          total_results: 25,
          search_time: 0.045,
        },
      });
      mockProductsService.prototype.searchProducts = mockSearchProducts;

      const { result } = renderHook(() => useProductStore());

      const searchParams = {
        q: 'laptop',
        categories: ['electronics'],
        price_range: '50000,200000',
      };

      await act(async () => {
        await result.current.searchProducts(searchParams);
      });

      expect(mockSearchProducts).toHaveBeenCalledWith(searchParams);
      expect(result.current.products.length).toBe(1);
    });
  });
});