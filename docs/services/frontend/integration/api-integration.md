# Frontend API Integration Guide

**Author**: Frontend Engineering Team  
**Created**: 2025-09-29  
**Last Updated**: 2025-09-29  
**Version**: 1.0.0  
**Owner**: Frontend Engineering Team  
**Related**: [Architecture Overview](../architecture/overview.md)  
**Review Date**: 2025-12-29  

## Summary

Complete guide for API integration between the frontend application and backend services via the API Gateway, including authentication, error handling, and data flow patterns.

## API Architecture Overview

### Communication Flow
```
Frontend App → API Gateway (Port 8000) → Backend Services
     ↑              ↓
 Auth Middleware → JWT Validation → Service Routing
```

### Base Configuration
```typescript
// api.config.ts
export const apiConfig = {
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
};

// HTTP client setup
const apiClient = axios.create(apiConfig);
```

## Authentication Integration

### JWT Token Management
```typescript
// auth.service.ts
export class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post('/api/auth/login', credentials);
    
    // Tokens are set as HTTP-only cookies by the server
    return response.data;
  }

  async logout(): Promise<void> {
    await apiClient.post('/api/auth/logout');
    // Cookies are cleared by the server
  }

  async refreshToken(): Promise<void> {
    await apiClient.post('/api/auth/refresh');
    // New tokens set as cookies by server
  }
}
```

### Request Interceptors
```typescript
// Authentication interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Cookies are automatically included
    // No manual token handling needed
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        await authService.refreshToken();
        // Retry original request
        return apiClient.request(error.config);
      } catch (refreshError) {
        // Redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
```

## Service Integration Patterns

### Product Catalog Service
```typescript
// product.service.ts
export class ProductService {
  async getProducts(params?: ProductQuery): Promise<Product[]> {
    const response = await apiClient.get('/api/products', { params });
    return response.data;
  }

  async getProduct(id: string): Promise<Product> {
    const response = await apiClient.get(`/api/products/${id}`);
    return response.data;
  }

  async searchProducts(query: string): Promise<Product[]> {
    const response = await apiClient.get('/api/products/search', {
      params: { q: query }
    });
    return response.data;
  }
}
```

### Shopping Cart Service
```typescript
// cart.service.ts
export class CartService {
  async getCart(): Promise<Cart> {
    const response = await apiClient.get('/api/cart');
    return response.data;
  }

  async addToCart(productId: string, quantity: number): Promise<Cart> {
    const response = await apiClient.post('/api/cart/items', {
      productId,
      quantity
    });
    return response.data;
  }

  async updateCartItem(itemId: string, quantity: number): Promise<Cart> {
    const response = await apiClient.put(`/api/cart/items/${itemId}`, {
      quantity
    });
    return response.data;
  }

  async removeFromCart(itemId: string): Promise<Cart> {
    const response = await apiClient.delete(`/api/cart/items/${itemId}`);
    return response.data;
  }
}
```

### Order Service
```typescript
// order.service.ts
export class OrderService {
  async createOrder(orderData: CreateOrderRequest): Promise<Order> {
    const response = await apiClient.post('/api/orders', orderData);
    return response.data;
  }

  async getOrders(): Promise<Order[]> {
    const response = await apiClient.get('/api/orders');
    return response.data;
  }

  async getOrder(id: string): Promise<Order> {
    const response = await apiClient.get(`/api/orders/${id}`);
    return response.data;
  }

  async cancelOrder(id: string): Promise<Order> {
    const response = await apiClient.post(`/api/orders/${id}/cancel`);
    return response.data;
  }
}
```

## Error Handling Strategy

### Error Types and Handling
```typescript
// error.types.ts
export interface ApiError {
  message: string;
  code: string;
  status: number;
  details?: Record<string, any>;
}

// error.handler.ts
export class ApiErrorHandler {
  static handle(error: AxiosError): ApiError {
    if (error.response) {
      // Server responded with error status
      return {
        message: error.response.data?.message || 'Server error occurred',
        code: error.response.data?.code || 'SERVER_ERROR',
        status: error.response.status,
        details: error.response.data?.details
      };
    } else if (error.request) {
      // Request made but no response received
      return {
        message: 'Network error - please check your connection',
        code: 'NETWORK_ERROR',
        status: 0
      };
    } else {
      // Something else happened
      return {
        message: error.message || 'Unknown error occurred',
        code: 'UNKNOWN_ERROR',
        status: 0
      };
    }
  }
}
```

### Retry Logic
```typescript
// retry.interceptor.ts
const retryConfig = {
  retries: 3,
  retryDelay: (retryCount: number) => Math.pow(2, retryCount) * 1000,
  retryCondition: (error: AxiosError) => {
    return (
      !error.response ||
      error.response.status >= 500 ||
      error.response.status === 429
    );
  }
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    
    if (!config || !retryConfig.retryCondition(error)) {
      return Promise.reject(error);
    }

    config.retryCount = config.retryCount || 0;
    
    if (config.retryCount >= retryConfig.retries) {
      return Promise.reject(error);
    }

    config.retryCount++;
    
    const delay = retryConfig.retryDelay(config.retryCount);
    await new Promise(resolve => setTimeout(resolve, delay));
    
    return apiClient.request(config);
  }
);
```

## Data Caching Strategy

### React Query Integration
```typescript
// hooks/useProducts.ts
export const useProducts = (params?: ProductQuery) => {
  return useQuery({
    queryKey: ['products', params],
    queryFn: () => productService.getProducts(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
};

// hooks/useCart.ts
export const useCart = () => {
  const queryClient = useQueryClient();
  
  const cartQuery = useQuery({
    queryKey: ['cart'],
    queryFn: cartService.getCart,
    staleTime: 0, // Always fresh
  });

  const addToCartMutation = useMutation({
    mutationFn: ({ productId, quantity }: AddToCartParams) => 
      cartService.addToCart(productId, quantity),
    onSuccess: (updatedCart) => {
      queryClient.setQueryData(['cart'], updatedCart);
    },
  });

  return {
    cart: cartQuery.data,
    isLoading: cartQuery.isLoading,
    error: cartQuery.error,
    addToCart: addToCartMutation.mutate,
    isAddingToCart: addToCartMutation.isLoading,
  };
};
```

## Real-time Updates

### WebSocket Integration
```typescript
// websocket.service.ts
export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect(url: string) {
    this.ws = new WebSocket(url);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.ws.onclose = () => {
      this.handleReconnect();
    };
  }

  private handleMessage(data: any) {
    switch (data.type) {
      case 'ORDER_STATUS_UPDATE':
        // Update order status in cache
        queryClient.invalidateQueries(['orders']);
        break;
      case 'CART_UPDATE':
        // Update cart data
        queryClient.invalidateQueries(['cart']);
        break;
      case 'NOTIFICATION':
        // Show notification to user
        toast.info(data.message);
        break;
    }
  }
}
```

## API Documentation Integration

### TypeScript Types from OpenAPI
```typescript
// Generated from OpenAPI specs
export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  imageUrl: string;
  inStock: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Cart {
  id: string;
  items: CartItem[];
  subtotal: number;
  tax: number;
  total: number;
  updatedAt: string;
}

export interface Order {
  id: string;
  status: OrderStatus;
  items: OrderItem[];
  shippingAddress: Address;
  billingAddress: Address;
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
  createdAt: string;
  updatedAt: string;
}
```

---
**API Integration Owner**: Frontend Engineering Team  
**Next Review**: 2025-12-29