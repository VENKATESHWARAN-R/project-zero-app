/**
 * Product Browsing Flow Integration Tests
 * Tests for complete product browsing and filtering workflow
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ProductList } from '@/components/product/ProductList';
import { ProductCard } from '@/components/product/ProductCard';
import { ProductsService } from '@/services/products';

// Mock the products service
jest.mock('@/services/products');

const mockProductsService = ProductsService as jest.MockedClass<typeof ProductsService>;

const mockProducts = [
  {
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
  },
  {
    id: 'product-2',
    name: 'Wireless Gaming Mouse',
    description: 'RGB wireless gaming mouse',
    price: 7999,
    currency: 'USD',
    category: 'accessories',
    image_url: 'https://example.com/mouse.jpg',
    in_stock: true,
    stock_quantity: 25,
    created_at: '2025-09-24T10:00:00Z',
    updated_at: '2025-09-24T10:00:00Z',
  },
];

const mockCategories = [
  {
    id: 'cat-1',
    name: 'Electronics',
    slug: 'electronics',
    description: 'Electronic devices',
    parent_id: null,
    product_count: 25,
  },
  {
    id: 'cat-2',
    name: 'Accessories',
    slug: 'accessories',
    description: 'Computer accessories',
    parent_id: null,
    product_count: 15,
  },
];

const mockProductsResponse = {
  products: mockProducts,
  pagination: {
    page: 1,
    limit: 20,
    total: 2,
    total_pages: 1,
    has_next: false,
    has_prev: false,
  },
  filters_applied: {},
};

const mockDetailedProduct = {
  ...mockProducts[0],
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

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => '/products',
  useSearchParams: () => new URLSearchParams(),
}));

const TestWrapper = ({ children }: { children: React.ReactNode }) => <>{children}</>;

describe('Product Browsing Flow Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Product Listing', () => {
    it('should load and display products on page load', async () => {
      // Mock products API
      const mockGetProducts = jest.fn().mockResolvedValue(mockProductsResponse);
      const mockGetCategories = jest.fn().mockResolvedValue({ categories: mockCategories });
      mockProductsService.prototype.getProducts = mockGetProducts;
      mockProductsService.prototype.getCategories = mockGetCategories;

      render(
        <TestWrapper>
          <ProductList products={mockProducts} categories={mockCategories} />
        </TestWrapper>
      );

      // Wait for products to load
      await waitFor(() => {
        expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
        expect(screen.getByText('Wireless Gaming Mouse')).toBeInTheDocument();
      });

      // Check API calls
      expect(mockGetProducts).toHaveBeenCalledWith({});
      expect(mockGetCategories).toHaveBeenCalled();

      // Check product information is displayed
      expect(screen.getByText('$1,499.99')).toBeInTheDocument();
      expect(screen.getByText('$79.99')).toBeInTheDocument();
      expect(screen.getAllByText(/in stock/i)).toHaveLength(2);
    });

    it('should show loading state while fetching products', async () => {
      // Mock delayed API response
      const mockGetProducts = jest.fn().mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockProductsResponse), 100))
      );
      const mockGetCategories = jest.fn().mockResolvedValue({ categories: mockCategories });
      mockProductsService.prototype.getProducts = mockGetProducts;
      mockProductsService.prototype.getCategories = mockGetCategories;

      render(
        <TestWrapper>
          <ProductList products={mockProducts} categories={mockCategories} />
        </TestWrapper>
      );

      // Check loading state
      expect(screen.getByText(/loading/i)).toBeInTheDocument();

      // Wait for products to load
      await waitFor(
        () => {
          expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
        },
        { timeout: 200 }
      );

      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });

    it('should handle product loading errors', async () => {
      // Mock API error
      const mockGetProducts = jest.fn().mockRejectedValue(new Error('Failed to load products'));
      const mockGetCategories = jest.fn().mockResolvedValue({ categories: mockCategories });
      mockProductsService.prototype.getProducts = mockGetProducts;
      mockProductsService.prototype.getCategories = mockGetCategories;

      render(
        <TestWrapper>
          <ProductList products={mockProducts} categories={mockCategories} />
        </TestWrapper>
      );

      // Wait for error to appear
      await waitFor(() => {
        expect(screen.getByText(/failed to load products/i)).toBeInTheDocument();
      });
    });
  });

  describe('Product Filtering', () => {
    it('should filter products by category', async () => {
      const user = userEvent.setup();

      // Mock filtered response
      const filteredResponse = {
        ...mockProductsResponse,
        products: [mockProducts[0]], // Only electronics
        filters_applied: { category: 'electronics' },
      };

      const mockGetProducts = jest.fn().mockResolvedValueOnce(mockProductsResponse);
      const mockGetCategories = jest.fn().mockResolvedValue({ categories: mockCategories });
      mockProductsService.prototype.getProducts = mockGetProducts;
      mockProductsService.prototype.getCategories = mockGetCategories;

      render(
        <TestWrapper>
          <ProductList products={mockProducts} categories={mockCategories} />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
      });

      // Mock filtered API response for category filter
      mockGetProducts.mockResolvedValueOnce(filteredResponse);

      // Filter by electronics category
      await user.click(screen.getByText('Electronics'));

      // Wait for filtered results
      await waitFor(() => {
        expect(mockGetProducts).toHaveBeenCalledWith({ category: 'electronics' });
      });

      // Check filter is applied
      expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
      expect(screen.queryByText('Wireless Gaming Mouse')).not.toBeInTheDocument();
    });

    it('should search products by query', async () => {
      const user = userEvent.setup();

      // Mock search response
      const searchResponse = {
        ...mockProductsResponse,
        products: [mockProducts[1]], // Only mouse
        filters_applied: { search: 'mouse' },
      };

      const mockGetProducts = jest.fn().mockResolvedValueOnce(mockProductsResponse);
      const mockGetCategories = jest.fn().mockResolvedValue({ categories: mockCategories });
      mockProductsService.prototype.getProducts = mockGetProducts;
      mockProductsService.prototype.getCategories = mockGetCategories;

      render(
        <TestWrapper>
          <ProductList products={mockProducts} categories={mockCategories} />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
      });

      // Mock search API response
      mockGetProducts.mockResolvedValueOnce(searchResponse);

      // Search for "mouse"
      const searchInput = screen.getByPlaceholderText(/search products/i);
      await user.type(searchInput, 'mouse');
      await user.keyboard('{Enter}');

      // Wait for search results
      await waitFor(() => {
        expect(mockGetProducts).toHaveBeenCalledWith({ search: 'mouse' });
      });

      // Check search results
      expect(screen.getByText('Wireless Gaming Mouse')).toBeInTheDocument();
      expect(screen.queryByText('Gaming Laptop Pro')).not.toBeInTheDocument();
    });

    it('should filter products by price range', async () => {
      const user = userEvent.setup();

      // Mock price filtered response
      const priceFilteredResponse = {
        ...mockProductsResponse,
        products: [mockProducts[1]], // Only mouse under $100
        filters_applied: { min_price: 0, max_price: 10000 },
      };

      const mockGetProducts = jest.fn().mockResolvedValueOnce(mockProductsResponse);
      const mockGetCategories = jest.fn().mockResolvedValue({ categories: mockCategories });
      mockProductsService.prototype.getProducts = mockGetProducts;
      mockProductsService.prototype.getCategories = mockGetCategories;

      render(
        <TestWrapper>
          <ProductList products={mockProducts} categories={mockCategories} />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
      });

      // Mock price filter API response
      mockGetProducts.mockResolvedValueOnce(priceFilteredResponse);

      // Set price range filter (0-100)
      const minPriceInput = screen.getByLabelText(/minimum price/i);
      const maxPriceInput = screen.getByLabelText(/maximum price/i);

      await user.clear(minPriceInput);
      await user.type(minPriceInput, '0');
      await user.clear(maxPriceInput);
      await user.type(maxPriceInput, '100');

      await user.click(screen.getByText(/apply filters/i));

      // Wait for filtered results
      await waitFor(() => {
        expect(mockGetProducts).toHaveBeenCalledWith({ min_price: 0, max_price: 10000 });
      });
    });

    it('should clear all filters', async () => {
      const user = userEvent.setup();

      const mockGetProducts = jest.fn().mockResolvedValueOnce(mockProductsResponse);
      const mockGetCategories = jest.fn().mockResolvedValue({ categories: mockCategories });
      mockProductsService.prototype.getProducts = mockGetProducts;
      mockProductsService.prototype.getCategories = mockGetCategories;

      render(
        <TestWrapper>
          <ProductList products={mockProducts} categories={mockCategories} />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
      });

      // Apply some filters first
      await user.click(screen.getByText('Electronics'));

      await waitFor(() => {
        expect(mockGetProducts).toHaveBeenCalledTimes(2); // Initial + filter
      });

      // Mock clear filters response
      mockGetProducts.mockResolvedValueOnce(mockProductsResponse);

      // Clear filters
      await user.click(screen.getByText(/clear filters/i));

      // Wait for results
      await waitFor(() => {
        expect(mockGetProducts).toHaveBeenCalledWith({});
      });
    });
  });

  describe('Product Detail View', () => {
    it('should load and display product details', async () => {
      // Mock product detail API
      const mockGetProduct = jest.fn().mockResolvedValue(mockDetailedProduct);
      mockProductsService.prototype.getProduct = mockGetProduct;

      // Mock URL params
      const mockParams = { id: 'product-1' };

      render(
        <TestWrapper>
          <ProductCard product={mockDetailedProduct} onAddToCart={jest.fn()} onViewDetails={jest.fn()} />
        </TestWrapper>
      );

      // Wait for product details to load
      await waitFor(() => {
        expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
        expect(screen.getByText('High-performance gaming laptop')).toBeInTheDocument();
      });

      // Check API call
      expect(mockGetProduct).toHaveBeenCalledWith('product-1');

      // Check detailed information
      expect(screen.getByText('Intel Core i9-13900H')).toBeInTheDocument();
      expect(screen.getByText('NVIDIA RTX 4080')).toBeInTheDocument();
      expect(screen.getByText('32GB DDR5')).toBeInTheDocument();
      expect(screen.getByText('1TB NVMe SSD')).toBeInTheDocument();

      // Check images
      expect(screen.getAllByRole('img')).toHaveLength(3); // Main + gallery images
    });

    it('should handle product not found', async () => {
      // Mock 404 error
      const mockGetProduct = jest.fn().mockRejectedValue(new Error('Product not found'));
      mockProductsService.prototype.getProduct = mockGetProduct;

      const mockParams = { id: 'nonexistent-product' };

      render(
        <TestWrapper>
          <ProductCard product={mockDetailedProduct} onAddToCart={jest.fn()} onViewDetails={jest.fn()} />
        </TestWrapper>
      );

      // Wait for error
      await waitFor(() => {
        expect(screen.getByText(/product not found/i)).toBeInTheDocument();
      });
    });
  });

  describe('Product Navigation', () => {
    it('should navigate from product list to product detail', async () => {
      const user = userEvent.setup();
      const mockNavigate = jest.fn();

      // Mock navigation hook
      jest.doMock('next/navigation', () => ({
        useRouter: () => ({ push: mockNavigate }),
      }));

      const mockGetProducts = jest.fn().mockResolvedValue(mockProductsResponse);
      const mockGetCategories = jest.fn().mockResolvedValue({ categories: mockCategories });
      mockProductsService.prototype.getProducts = mockGetProducts;
      mockProductsService.prototype.getCategories = mockGetCategories;

      render(
        <TestWrapper>
          <ProductList products={mockProducts} categories={mockCategories} />
        </TestWrapper>
      );

      // Wait for products to load
      await waitFor(() => {
        expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
      });

      // Click on product
      await user.click(screen.getByText('View Details'));

      expect(mockNavigate).toHaveBeenCalledWith('/products/product-1');
    });
  });

  describe('Pagination', () => {
    it('should handle pagination navigation', async () => {
      const user = userEvent.setup();

      // Mock first page response
      const firstPageResponse = {
        ...mockProductsResponse,
        pagination: {
          page: 1,
          limit: 1,
          total: 2,
          total_pages: 2,
          has_next: true,
          has_prev: false,
        },
        products: [mockProducts[0]],
      };

      // Mock second page response
      const secondPageResponse = {
        ...mockProductsResponse,
        pagination: {
          page: 2,
          limit: 1,
          total: 2,
          total_pages: 2,
          has_next: false,
          has_prev: true,
        },
        products: [mockProducts[1]],
      };

      const mockGetProducts = jest.fn().mockResolvedValueOnce(firstPageResponse);
      const mockGetCategories = jest.fn().mockResolvedValue({ categories: mockCategories });
      mockProductsService.prototype.getProducts = mockGetProducts;
      mockProductsService.prototype.getCategories = mockGetCategories;

      render(
        <TestWrapper>
          <ProductList products={mockProducts} categories={mockCategories} />
        </TestWrapper>
      );

      // Wait for first page
      await waitFor(() => {
        expect(screen.getByText('Gaming Laptop Pro')).toBeInTheDocument();
      });

      // Mock second page API response
      mockGetProducts.mockResolvedValueOnce(secondPageResponse);

      // Navigate to next page
      await user.click(screen.getByText(/next/i));

      // Wait for second page
      await waitFor(() => {
        expect(mockGetProducts).toHaveBeenCalledWith({ page: 2 });
      });
    });
  });
});