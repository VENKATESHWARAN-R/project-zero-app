# Data Model: Next.js Frontend Application

**Date**: 2025-09-24
**Status**: Complete

## Entity Definitions

### 1. User
Represents an authenticated user with account information.

**Fields**:
- `id`: string (unique identifier)
- `email`: string (unique, validated email address)
- `firstName`: string (user's first name)
- `lastName`: string (user's last name)
- `createdAt`: string (ISO date string)
- `updatedAt`: string (ISO date string)

**Validation Rules**:
- Email must be valid email format
- First name and last name required, 1-50 characters
- All string fields must be sanitized for XSS

**State Transitions**:
- Guest → Registered (via registration)
- Registered → Authenticated (via login)
- Authenticated → Guest (via logout)

### 2. Product
Represents a catalog item available for purchase.

**Fields**:
- `id`: string (unique identifier)
- `name`: string (product name)
- `description`: string (detailed product description)
- `price`: number (price in cents to avoid floating point issues)
- `currency`: string (currency code, default: "USD")
- `category`: string (product category)
- `imageUrl`: string (product image URL)
- `inStock`: boolean (availability status)
- `stockQuantity`: number (available quantity)
- `createdAt`: string (ISO date string)
- `updatedAt`: string (ISO date string)

**Validation Rules**:
- Name required, 1-200 characters
- Price must be positive integer (cents)
- Category must be from predefined list
- Stock quantity must be non-negative integer

**State Transitions**:
- In Stock → Out of Stock (when stockQuantity reaches 0)
- Out of Stock → In Stock (when stockQuantity > 0)

### 3. CartItem
Represents a product added to user's shopping cart.

**Fields**:
- `id`: string (unique identifier)
- `productId`: string (reference to Product)
- `product`: Product (embedded product data)
- `quantity`: number (number of items)
- `addedAt`: string (ISO date string when added to cart)

**Validation Rules**:
- Quantity must be positive integer
- Quantity cannot exceed product stock
- Product must exist and be in stock

**State Transitions**:
- Added → Updated (quantity change)
- Added → Removed (quantity set to 0 or explicit removal)

### 4. Cart
Represents user's shopping cart containing multiple items.

**Fields**:
- `id`: string (unique identifier)
- `userId`: string (reference to User)
- `items`: CartItem[] (array of cart items)
- `totalAmount`: number (calculated total in cents)
- `itemCount`: number (total number of items)
- `createdAt`: string (ISO date string)
- `updatedAt`: string (ISO date string)

**Validation Rules**:
- Items array cannot be null
- Total amount calculated from item prices and quantities
- Item count calculated from item quantities

**State Transitions**:
- Empty → Has Items (first item added)
- Has Items → Empty (all items removed)
- Has Items → Checkout Ready (validation passed)

### 5. Category
Represents product categorization for filtering and organization.

**Fields**:
- `id`: string (unique identifier)
- `name`: string (category name)
- `slug`: string (URL-friendly identifier)
- `description`: string (optional category description)
- `parentId`: string | null (for hierarchical categories)

**Validation Rules**:
- Name required, 1-100 characters
- Slug must be URL-safe
- Parent category must exist if specified

### 6. AuthToken
Represents JWT authentication tokens for user session management.

**Fields**:
- `accessToken`: string (JWT access token)
- `refreshToken`: string (JWT refresh token)
- `expiresAt`: number (access token expiration timestamp)
- `tokenType`: string (always "Bearer")

**Validation Rules**:
- Tokens must be valid JWT format
- Expiration time must be future timestamp
- Token type must be "Bearer"

**State Transitions**:
- Valid → Expired (when current time > expiresAt)
- Expired → Refreshed (via refresh token exchange)
- Valid → Revoked (via logout)

## Client-Side State Structure

### 1. Authentication Store (Zustand)
```typescript
interface AuthState {
  user: User | null
  tokens: AuthToken | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
  clearError: () => void
}
```

### 2. Cart Store (Zustand)
```typescript
interface CartState {
  cart: Cart | null
  isLoading: boolean
  error: string | null

  // Actions
  loadCart: () => Promise<void>
  addItem: (productId: string, quantity: number) => Promise<void>
  updateItemQuantity: (itemId: string, quantity: number) => Promise<void>
  removeItem: (itemId: string) => Promise<void>
  clearCart: () => Promise<void>
  clearError: () => void
}
```

### 3. Product Store (Zustand)
```typescript
interface ProductState {
  products: Product[]
  categories: Category[]
  currentProduct: Product | null
  isLoading: boolean
  error: string | null
  filters: {
    category: string | null
    search: string
    priceRange: [number, number] | null
  }

  // Actions
  loadProducts: (filters?: ProductFilters) => Promise<void>
  loadProduct: (id: string) => Promise<void>
  loadCategories: () => Promise<void>
  setFilters: (filters: Partial<ProductFilters>) => void
  clearError: () => void
}
```

## Data Flow Patterns

### 1. Authentication Flow
1. User submits login form → AuthStore.login()
2. API call to /auth/login → Store tokens
3. Set user state and isAuthenticated flag
4. Redirect to intended page or home

### 2. Product Browsing Flow
1. User visits products page → ProductStore.loadProducts()
2. User applies filters → ProductStore.setFilters() → loadProducts()
3. User clicks product → Navigate to product detail → ProductStore.loadProduct()

### 3. Cart Management Flow
1. User clicks "Add to Cart" → Check authentication
2. If authenticated → CartStore.addItem() → API call
3. Update cart state and item count
4. Show success feedback

### 4. Checkout Preparation Flow
1. User visits cart page → CartStore.loadCart()
2. User updates quantities → CartStore.updateItemQuantity()
3. Calculate totals and validate stock
4. Prepare for checkout process

## Persistence Strategy

### Client-Side Storage
- **localStorage**: JWT tokens, user preferences
- **sessionStorage**: Temporary form data
- **Memory**: Product cache, current session data

### Server Synchronization
- Cart state synchronized with backend on all modifications
- Product data cached with TTL-based invalidation
- User profile synchronized on login and updates

## Error Handling

### Validation Errors
- Client-side validation before API calls
- Server validation error display
- Form field highlighting for errors

### Network Errors
- Retry logic for failed requests
- Offline state detection
- Graceful degradation for unavailable services

### Authentication Errors
- Automatic token refresh on 401 errors
- Redirect to login on refresh failure
- Clear sensitive data on authentication errors