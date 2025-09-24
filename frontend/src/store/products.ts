/**
 * Products store using Zustand
 * Manages product catalog state and actions
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { Product, ProductFilters, Category } from '@/types/product';
import { ProductsService } from '@/services/products';

const getErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof Error && error.message) {
    return error.message;
  }

  if (typeof error === 'object' && error !== null) {
    const detail = (error as { detail?: unknown }).detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }

    const message = (error as { message?: unknown }).message;
    if (typeof message === 'string' && message.trim()) {
      return message;
    }
  }

  return fallback;
};

interface ProductState {
  // State
  products: Product[];
  categories: Category[];
  currentProduct: Product | null;
  isLoading: boolean;
  error: string | null;
  filters: ProductFilters;
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
  lastUpdated: number | null;

  // Actions
  loadProducts: (filters?: Partial<ProductFilters>) => Promise<void>;
  loadProduct: (id: string) => Promise<void>;
  loadCategories: () => Promise<void>;
  searchProducts: (query: string, filters?: Partial<ProductFilters>) => Promise<void>;
  setFilters: (filters: Partial<ProductFilters>) => void;
  resetFilters: () => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  clearCurrentProduct: () => void;
}

const initialFilters: ProductFilters = {
  category: '',
  search: '',
  min_price: undefined,
  max_price: undefined,
  in_stock: undefined,
  page: 1,
  limit: 20,
  sort: 'name',
  order: 'asc',
};

export const useProductsStore = create<ProductState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    products: [],
    categories: [],
    currentProduct: null,
    isLoading: false,
    error: null,
    filters: { ...initialFilters },
    pagination: {
      page: 1,
      limit: 20,
      total: 0,
      totalPages: 0,
      hasNext: false,
      hasPrev: false,
    },
    lastUpdated: null,

    // Actions
    loadProducts: async (filters?: Partial<ProductFilters>) => {
      set({ isLoading: true, error: null });

      try {
        // Update filters if provided
        const currentFilters = get().filters;
        const updatedFilters = filters ? { ...currentFilters, ...filters } : currentFilters;

        if (filters) {
          set({ filters: updatedFilters });
        }

        const response = await ProductsService.getProducts(updatedFilters);

        // Transform products if needed
        const transformedProducts = response.products.map(product =>
          ProductsService.transformProductFromApi(product)
        );

        set({
          products: transformedProducts,
          pagination: response.pagination,
          isLoading: false,
          error: null,
          lastUpdated: Date.now(),
        });

      } catch (error: unknown) {
        set({
          products: [],
          isLoading: false,
          error: getErrorMessage(error, 'Failed to load products'),
        });
      }
    },

    loadProduct: async (id: string) => {
      set({ isLoading: true, error: null });

      try {
        const product = await ProductsService.getProduct(id);

        set({
          currentProduct: product,
          isLoading: false,
          error: null,
        });

      } catch (error: unknown) {
        set({
          currentProduct: null,
          isLoading: false,
          error: getErrorMessage(error, 'Failed to load product'),
        });
      }
    },

    loadCategories: async () => {
      try {
        const response = await ProductsService.getCategories();

        set({
          categories: response.categories,
          error: null,
        });

      } catch (error: unknown) {
        set({
          categories: [],
          error: getErrorMessage(error, 'Failed to load categories'),
        });
      }
    },

    searchProducts: async (query: string, filters?: Partial<ProductFilters>) => {
      set({ isLoading: true, error: null });

      try {
        const currentFilters = get().filters;
        const searchFilters = {
          ...currentFilters,
          search: query,
          ...filters,
          page: 1, // Reset to first page for new search
        };

        set({ filters: searchFilters });

        const response = await ProductsService.searchProducts(query, searchFilters);

        // Transform products if needed
        const transformedProducts = response.products.map(product =>
          ProductsService.transformProductFromApi(product)
        );

        set({
          products: transformedProducts,
          pagination: response.pagination,
          isLoading: false,
          error: null,
          lastUpdated: Date.now(),
        });

      } catch (error: unknown) {
        set({
          products: [],
          isLoading: false,
          error: getErrorMessage(error, 'Search failed'),
        });
      }
    },

    setFilters: (filters: Partial<ProductFilters>) => {
      const currentFilters = get().filters;
      const updatedFilters = { ...currentFilters, ...filters };

      set({ filters: updatedFilters });

      // Auto-reload products when filters change
      get().loadProducts();
    },

    resetFilters: () => {
      set({ filters: { ...initialFilters } });
      get().loadProducts();
    },

    clearError: () => {
      set({ error: null });
    },

    setLoading: (loading: boolean) => {
      set({ isLoading: loading });
    },

    clearCurrentProduct: () => {
      set({ currentProduct: null });
    },
  }))
);

// Computed values and selectors
export const useProductsSelectors = () => {
  const products = useProductsStore(state => state.products);
  const categories = useProductsStore(state => state.categories);
  const currentProduct = useProductsStore(state => state.currentProduct);
  const isLoading = useProductsStore(state => state.isLoading);
  const error = useProductsStore(state => state.error);
  const filters = useProductsStore(state => state.filters);
  const pagination = useProductsStore(state => state.pagination);

  // Derived values
  const availableProducts = products.filter(product => ProductsService.isProductAvailable(product));
  const outOfStockProducts = products.filter(product => !ProductsService.isProductAvailable(product));
  const priceRange = ProductsService.getPriceRange(products);
  const uniqueCategories = ProductsService.getUniqueCategories(products);

  return {
    products,
    categories,
    currentProduct,
    isLoading,
    error,
    filters,
    pagination,
    availableProducts,
    outOfStockProducts,
    priceRange,
    uniqueCategories,
    hasProducts: products.length > 0,
    isEmpty: products.length === 0 && !isLoading,
  };
};

// Hook for product actions
export const useProductsActions = () => {
  const {
    loadProducts,
    loadProduct,
    loadCategories,
    searchProducts,
    setFilters,
    resetFilters,
    clearError,
    clearCurrentProduct,
  } = useProductsStore();

  return {
    loadProducts,
    loadProduct,
    loadCategories,
    searchProducts,
    setFilters,
    resetFilters,
    clearError,
    clearCurrentProduct,
  };
};

// Utility functions for filtering and sorting
export const useProductUtils = () => {
  const products = useProductsStore(state => state.products);

  const filterProducts = (filterFn: (product: Product) => boolean) => {
    return products.filter(filterFn);
  };

  const sortProducts = (
    sortBy: 'name' | 'price' | 'created_at' = 'name',
    order: 'asc' | 'desc' = 'asc'
  ) => {
    return ProductsService.sortProducts(products, sortBy, order);
  };

  const searchProductsLocally = (query: string) => {
    return ProductsService.searchProductsLocally(products, query);
  };

  const getProductsByCategory = (categorySlug: string) => {
    return ProductsService.filterByCategory(products, categorySlug);
  };

  const getProductsByPriceRange = (minPrice: number, maxPrice: number) => {
    return ProductsService.filterByPriceRange(products, minPrice, maxPrice);
  };

  const getAvailableProducts = () => {
    return ProductsService.filterByAvailability(products, true);
  };

  return {
    filterProducts,
    sortProducts,
    searchProductsLocally,
    getProductsByCategory,
    getProductsByPriceRange,
    getAvailableProducts,
  };
};

export const useProductStore = useProductsStore;
export default useProductsStore;
