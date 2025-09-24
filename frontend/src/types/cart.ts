/**
 * Cart type definitions
 * Based on cart API contract and data model
 */

export interface CartItem {
  id: string;
  productId: string;
  quantity: number;
  addedAt: string;
  product: {
    id: string;
    name: string;
    description?: string;
    price: number;
    currency: string;
    category?: string;
    imageUrl: string;
    images?: string[];
    specifications?: Record<string, any>;
    inStock: boolean;
    stockQuantity: number;
    createdAt?: string;
    updatedAt?: string;
  };
}

export interface Cart {
  id: string;
  userId: string;
  items: CartItem[];
  totalAmount: number; // Total in cents
  itemCount: number;
  currency: string;
  createdAt: string;
  updatedAt: string;
}

export interface AddItemRequest {
  product_id: string;
  quantity: number;
}

export interface UpdateItemRequest {
  quantity: number;
}

export interface CartResponse {
  id: string;
  user_id: string;
  items: {
    id: string;
    product_id: string;
    quantity: number;
    added_at: string;
    product: {
      id: string;
      name: string;
      price: number;
      currency: string;
      image_url: string;
      in_stock: boolean;
      stock_quantity: number;
    };
  }[];
  total_amount: number;
  item_count: number;
  currency: string;
  created_at: string;
  updated_at: string;
}

export interface AddItemResponse {
  id: string;
  product_id: string;
  quantity: number;
  added_at: string;
  product: {
    id: string;
    name: string;
    price: number;
    currency: string;
    image_url: string;
    in_stock: boolean;
    stock_quantity: number;
  };
  cart_summary: {
    total_amount: number;
    item_count: number;
  };
}

export interface UpdateItemResponse {
  id: string;
  product_id: string;
  quantity: number;
  added_at: string;
  product: {
    id: string;
    name: string;
    price: number;
    currency: string;
    image_url: string;
    in_stock: boolean;
    stock_quantity: number;
  };
  cart_summary: {
    total_amount: number;
    item_count: number;
  };
}

export interface RemoveItemResponse {
  message: string;
  removed_item_id: string;
  cart_summary: {
    total_amount: number;
    item_count: number;
  };
}

export interface ClearCartResponse {
  message: string;
  cart_summary: {
    total_amount: number;
    item_count: number;
  };
}

export interface CartSummaryResponse {
  item_count: number;
  total_amount: number;
  currency: string;
  updated_at: string;
}

export interface CartValidationItem {
  cart_item_id: string;
  product_id: string;
  status: 'valid' | 'insufficient_stock' | 'out_of_stock' | 'price_changed' | 'unavailable';
  requested_quantity: number;
  available_quantity: number;
  current_price: number;
  price_changed: boolean;
}

export interface CartValidationIssue {
  type: 'insufficient_stock' | 'out_of_stock' | 'price_changed' | 'unavailable';
  cart_item_id: string;
  message: string;
}

export interface ValidateCartResponse {
  valid: boolean;
  items: CartValidationItem[];
  total_amount: number;
  issues: CartValidationIssue[];
}

export interface BulkAddItemsRequest {
  items: {
    product_id: string;
    quantity: number;
  }[];
}

export interface BulkAddItemsResponse {
  added_items: {
    id: string;
    product_id: string;
    quantity: number;
    status: 'added' | 'updated';
  }[];
  failed_items: {
    product_id: string;
    error: string;
  }[];
  cart_summary: {
    total_amount: number;
    item_count: number;
  };
}

// Additional types for services
export interface UpdateCartItemRequest {
  quantity: number;
}

export interface AddToCartRequest {
  product_id: string;
  quantity: number;
}

export interface CartSummary {
  item_count: number;
  total_amount: number;
  currency: string;
  updated_at: string;
}

export interface BulkAddToCartRequest {
  items: Array<{
    product_id: string;
    quantity: number;
  }>;
}

export interface CartValidationResponse {
  valid: boolean;
  items: Array<{
    cart_item_id: string;
    product_id: string;
    status: string;
    requested_quantity: number;
    available_quantity: number;
    current_price: number;
    price_changed: boolean;
  }>;
  total_amount: number;
  issues: CartValidationIssue[];
}