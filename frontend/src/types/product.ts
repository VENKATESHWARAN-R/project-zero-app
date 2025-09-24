/**
 * Product type definitions
 * Based on products API contract and data model
 */

export interface Product {
  id: string;
  name: string;
  description: string;
  price: number; // Price in cents
  currency: string;
  category: string;
  imageUrl: string;
  images?: string[];
  inStock: boolean;
  stockQuantity: number;
  specifications?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string;
  parentId: string | null;
  productCount: number;
}

export interface ProductFilters {
  category?: string | null;
  search?: string;
  min_price?: number;
  max_price?: number;
  in_stock?: boolean;
  page?: number;
  limit?: number;
  sort?: 'name' | 'price' | 'created_at';
  order?: 'asc' | 'desc';
  priceRange?: [number, number] | null;
}

export interface Pagination {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  total_pages: number;
  hasNext: boolean;
  hasPrev: boolean;
  has_next: boolean;
  has_prev: boolean;
}

// Alias for better consistency - removing empty interface that extends SearchProductsResponse
export type ProductSearchResponse = SearchProductsResponse;

export interface ProductsResponse {
  products: {
    id: string;
    name: string;
    description: string;
    price: number;
    currency: string;
    category: string;
    image_url: string;
    in_stock: boolean;
    stock_quantity: number;
    created_at: string;
    updated_at: string;
  }[];
  pagination: Pagination;
  filters_applied?: Partial<ProductFilters>;
}

export interface ProductDetailResponse {
  id: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  category: string;
  image_url: string;
  images?: string[];
  in_stock: boolean;
  stock_quantity: number;
  specifications?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CategoriesResponse {
  categories: {
    id: string;
    name: string;
    slug: string;
    description: string;
    parent_id: string | null;
    product_count: number;
  }[];
}

export interface RelatedProductsResponse {
  related_products: {
    id: string;
    name: string;
    price: number;
    currency: string;
    image_url: string;
    in_stock: boolean;
  }[];
}

export interface SearchProductsParams {
  q: string;
  categories?: string[];
  price_range?: string;
  brands?: string[];
  in_stock?: boolean;
  sort?: string;
  order?: string;
  page?: number;
  limit?: number;
}

export interface SearchFacet {
  categories: { slug: string; name: string; count: number }[];
  brands: { name: string; count: number }[];
  price_ranges: { min: number; max: number; count: number }[];
}

export interface SearchProductsResponse {
  products: Product[];
  facets: SearchFacet;
  pagination: Pagination;
  search_info: {
    query: string;
    total_results: number;
    search_time: number;
  };
}
