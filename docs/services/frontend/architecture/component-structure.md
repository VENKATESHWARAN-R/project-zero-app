# Frontend Component Structure

**Author**: Sarah Chen, Frontend Technical Lead  
**Created**: 2025-09-29  
**Last Updated**: 2025-09-29  
**Version**: 1.0.0  
**Owner**: Frontend Engineering Team  
**Related**: [Architecture Overview](./overview.md) | [API Integration](../integration/api-integration.md)  
**Review Date**: 2025-12-29  

## Summary

This document describes the component structure and organization of the Project Zero App frontend, including component hierarchy, design patterns, reusability strategies, and maintenance guidelines.

## Component Organization Philosophy

The frontend follows a hierarchical component organization based on atomic design principles, combining with feature-based organization for scalability and maintainability. Components are organized by their level of abstraction and reusability.

### Component Categories

1. **UI Components** (`src/components/ui/`): Basic, highly reusable building blocks
2. **Layout Components** (`src/components/layout/`): Structural components for page organization
3. **Feature Components** (`src/components/features/`): Business logic specific components
4. **Form Components** (`src/components/forms/`): Form-specific components with validation
5. **Page Components** (`src/app/*/page.tsx`): Top-level page components

## UI Component Library

### Base Components

Located in `src/components/ui/`, these are the atomic building blocks:

#### Button Component
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

// Usage
<Button variant="primary" size="lg" loading={isSubmitting}>
  Add to Cart
</Button>
```

#### Input Component
```typescript
interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number';
  placeholder?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  value: string;
  onChange: (value: string) => void;
}

// Usage
<Input
  type="email"
  placeholder="Enter your email"
  value={email}
  onChange={setEmail}
  error={emailError}
  required
/>
```

#### Card Component
```typescript
interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'outline' | 'filled';
  clickable?: boolean;
  onClick?: () => void;
}

// Usage
<Card variant="outline" clickable onClick={() => navigate('/product/123')}>
  <CardHeader>Product Title</CardHeader>
  <CardContent>Product description...</CardContent>
  <CardFooter>$29.99</CardFooter>
</Card>
```

### Composite Components

More complex UI components that combine base components:

#### Modal Component
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
}

// Implementation includes:
// - Focus management and keyboard navigation
// - Backdrop click handling
// - Escape key handling
// - Scroll lock when open
// - Animation transitions
```

#### DataTable Component
```typescript
interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  pagination?: PaginationConfig;
  sorting?: SortingConfig;
  filtering?: FilteringConfig;
  loading?: boolean;
  onRowClick?: (row: T) => void;
}

// Features:
// - Sortable columns
// - Filterable data
// - Pagination
// - Row selection
// - Loading states
// - Responsive design
```

## Layout Components

### Header Component

The main navigation header with responsive behavior:

```typescript
interface HeaderProps {
  user?: User;
  cartItemCount: number;
  onLoginClick: () => void;
  onLogoutClick: () => void;
  onCartClick: () => void;
}

// Features:
// - Responsive navigation menu
// - User authentication status display
// - Cart item counter
// - Search functionality
// - Mobile hamburger menu
```

### Navigation Component

```typescript
interface NavigationProps {
  items: NavItem[];
  currentPath: string;
  isMobile?: boolean;
  isOpen?: boolean;
  onToggle?: () => void;
}

// Navigation structure:
const navigationItems = [
  { label: 'Home', href: '/' },
  { label: 'Products', href: '/products', children: [
    { label: 'All Products', href: '/products' },
    { label: 'Electronics', href: '/products/category/electronics' },
    { label: 'Clothing', href: '/products/category/clothing' }
  ]},
  { label: 'Orders', href: '/orders', requiresAuth: true },
  { label: 'Profile', href: '/profile', requiresAuth: true }
];
```

### Footer Component

```typescript
interface FooterProps {
  links: FooterSection[];
  socialLinks: SocialLink[];
  newsletterSignup?: boolean;
}

// Footer sections:
const footerSections = [
  {
    title: 'Customer Service',
    links: [
      { label: 'Help Center', href: '/help' },
      { label: 'Returns', href: '/returns' },
      { label: 'Contact Us', href: '/contact' }
    ]
  },
  {
    title: 'Company',
    links: [
      { label: 'About Us', href: '/about' },
      { label: 'Careers', href: '/careers' },
      { label: 'Privacy Policy', href: '/privacy' }
    ]
  }
];
```

## Feature Components

### Product Components

#### ProductCard Component
```typescript
interface ProductCardProps {
  product: Product;
  onAddToCart: (productId: string) => void;
  onQuickView: (productId: string) => void;
  variant?: 'grid' | 'list';
  showQuickAdd?: boolean;
}

// Features:
// - Product image with lazy loading
// - Product title, price, and rating
// - Add to cart functionality
// - Quick view modal trigger
// - Wishlist toggle
// - Sale/discount indicators
```

#### ProductGrid Component
```typescript
interface ProductGridProps {
  products: Product[];
  loading?: boolean;
  onLoadMore?: () => void;
  hasMore?: boolean;
}

// Features:
// - Responsive grid layout
// - Infinite scroll or pagination
// - Loading skeletons
// - Empty state handling
// - Filter and sort integration
```

### Shopping Cart Components

#### CartItem Component
```typescript
interface CartItemProps {
  item: CartItem;
  onUpdateQuantity: (itemId: string, quantity: number) => void;
  onRemove: (itemId: string) => void;
  editable?: boolean;
}

// Features:
// - Product image and details
// - Quantity selector with validation
// - Price calculation
// - Remove item functionality
// - Availability status
```

#### CartSummary Component
```typescript
interface CartSummaryProps {
  items: CartItem[];
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
  onCheckout: () => void;
  checkoutDisabled?: boolean;
}

// Features:
// - Itemized cost breakdown
// - Promo code application
// - Shipping calculator
// - Tax calculation display
// - Checkout button with validation
```

### Authentication Components

#### LoginForm Component
```typescript
interface LoginFormProps {
  onSuccess: (user: User) => void;
  onError: (error: string) => void;
  redirectTo?: string;
}

// Features:
// - Email/password validation
// - Remember me functionality
// - Social login options
// - Forgot password link
// - Loading states and error handling
```

## Form Components

### Form Infrastructure

All forms use a consistent validation and error handling approach:

```typescript
// Base form hook
const useForm = <T>(initialValues: T, validationSchema: Schema<T>) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState<Partial<T>>({});
  const [touched, setTouched] = useState<Partial<T>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateField = (name: keyof T, value: any) => {
    // Validation logic
  };

  const handleSubmit = async (onSubmit: (values: T) => Promise<void>) => {
    // Submit handling with validation
  };

  return { values, errors, touched, isSubmitting, handleSubmit, setFieldValue };
};
```

### Specialized Form Components

#### CheckoutForm Component
```typescript
interface CheckoutFormProps {
  initialData?: Partial<CheckoutData>;
  onSubmit: (data: CheckoutData) => Promise<void>;
}

// Features:
// - Multi-step form with progress indicator
// - Address autocomplete
// - Payment method selection
// - Order summary integration
// - Form persistence across steps
```

#### ProfileForm Component
```typescript
interface ProfileFormProps {
  user: User;
  onUpdate: (updates: Partial<User>) => Promise<void>;
}

// Features:
// - Personal information editing
// - Address management
// - Password change
// - Email verification
// - Account deletion
```

## Component Design Patterns

### Compound Component Pattern

For complex components that need flexible composition:

```typescript
// ProductCard compound component
const ProductCard = ({ children, ...props }) => {
  return <div className="product-card" {...props}>{children}</div>;
};

ProductCard.Image = ({ src, alt, ...props }) => {
  return <img className="product-card__image" src={src} alt={alt} {...props} />;
};

ProductCard.Title = ({ children, ...props }) => {
  return <h3 className="product-card__title" {...props}>{children}</h3>;
};

ProductCard.Price = ({ price, currency = 'USD', ...props }) => {
  return <span className="product-card__price" {...props}>{formatPrice(price, currency)}</span>;
};

// Usage
<ProductCard>
  <ProductCard.Image src={product.image} alt={product.name} />
  <ProductCard.Title>{product.name}</ProductCard.Title>
  <ProductCard.Price price={product.price} />
</ProductCard>
```

### Render Props Pattern

For sharing stateful logic between components:

```typescript
interface DataFetcherProps<T> {
  url: string;
  children: (data: T | null, loading: boolean, error: string | null) => React.ReactNode;
}

const DataFetcher = <T,>({ url, children }: DataFetcherProps<T>) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, [url]);

  return children(data, loading, error);
};

// Usage
<DataFetcher<Product[]> url="/api/products">
  {(products, loading, error) => (
    <>
      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {products && <ProductGrid products={products} />}
    </>
  )}
</DataFetcher>
```

### Higher-Order Component Pattern

For cross-cutting concerns like authentication:

```typescript
const withAuth = <P extends object>(WrappedComponent: React.ComponentType<P>) => {
  return (props: P) => {
    const { user, isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
      return <LoadingSpinner />;
    }

    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }

    return <WrappedComponent {...props} user={user} />;
  };
};

// Usage
const ProtectedProfilePage = withAuth(ProfilePage);
```

## Component Testing Strategy

### Unit Testing

Each component should have comprehensive unit tests:

```typescript
// ProductCard.test.tsx
describe('ProductCard', () => {
  const mockProduct = {
    id: '1',
    name: 'Test Product',
    price: 29.99,
    image: '/test-image.jpg'
  };

  it('renders product information correctly', () => {
    render(<ProductCard product={mockProduct} onAddToCart={jest.fn()} />);
    
    expect(screen.getByText('Test Product')).toBeInTheDocument();
    expect(screen.getByText('$29.99')).toBeInTheDocument();
    expect(screen.getByAltText('Test Product')).toHaveAttribute('src', '/test-image.jpg');
  });

  it('calls onAddToCart when add to cart button is clicked', () => {
    const mockAddToCart = jest.fn();
    render(<ProductCard product={mockProduct} onAddToCart={mockAddToCart} />);
    
    fireEvent.click(screen.getByText('Add to Cart'));
    expect(mockAddToCart).toHaveBeenCalledWith(mockProduct.id);
  });

  it('shows loading state when adding to cart', () => {
    render(<ProductCard product={mockProduct} onAddToCart={jest.fn()} loading />);
    
    expect(screen.getByText('Adding...')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### Integration Testing

Test component interactions and data flow:

```typescript
// CheckoutFlow.integration.test.tsx
describe('Checkout Flow Integration', () => {
  it('completes full checkout process', async () => {
    const mockCart = [{ id: '1', quantity: 2, product: mockProduct }];
    
    render(<CheckoutPage />, {
      wrapper: ({ children }) => (
        <CartProvider initialCart={mockCart}>
          <AuthProvider user={mockUser}>
            {children}
          </AuthProvider>
        </CartProvider>
      )
    });

    // Test shipping address step
    await userEvent.type(screen.getByLabelText(/street address/i), '123 Main St');
    await userEvent.click(screen.getByText(/continue to payment/i));

    // Test payment step
    await userEvent.type(screen.getByLabelText(/card number/i), '4111111111111111');
    await userEvent.click(screen.getByText(/place order/i));

    // Verify order completion
    await waitFor(() => {
      expect(screen.getByText(/order placed successfully/i)).toBeInTheDocument();
    });
  });
});
```

## Performance Optimization

### Memoization Strategy

```typescript
// Expensive component with proper memoization
const ProductGrid = React.memo(({ products, filters }: ProductGridProps) => {
  const filteredProducts = useMemo(() => {
    return products.filter(product => 
      applyFilters(product, filters)
    );
  }, [products, filters]);

  const sortedProducts = useMemo(() => {
    return sortProducts(filteredProducts, filters.sortBy);
  }, [filteredProducts, filters.sortBy]);

  return (
    <div className="product-grid">
      {sortedProducts.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison for props
  return (
    prevProps.products.length === nextProps.products.length &&
    JSON.stringify(prevProps.filters) === JSON.stringify(nextProps.filters)
  );
});
```

### Lazy Loading

```typescript
// Lazy loaded components for code splitting
const ProductDetailsModal = React.lazy(() => import('./ProductDetailsModal'));
const CheckoutForm = React.lazy(() => import('./CheckoutForm'));

// Usage with Suspense
<Suspense fallback={<ComponentSkeleton />}>
  <ProductDetailsModal productId={selectedProductId} />
</Suspense>
```

### Virtual Scrolling

For large lists:

```typescript
import { FixedSizeList as List } from 'react-window';

const VirtualizedProductList = ({ products }: { products: Product[] }) => (
  <List
    height={600}
    itemCount={products.length}
    itemSize={200}
    width="100%"
  >
    {({ index, style }) => (
      <div style={style}>
        <ProductCard product={products[index]} />
      </div>
    )}
  </List>
);
```

## Accessibility Implementation

### ARIA Standards

All components implement proper ARIA attributes:

```typescript
const Button = ({ children, disabled, loading, ...props }: ButtonProps) => (
  <button
    {...props}
    disabled={disabled || loading}
    aria-disabled={disabled || loading}
    aria-busy={loading}
    aria-describedby={loading ? 'button-loading-text' : undefined}
  >
    {loading ? (
      <>
        <Spinner aria-hidden="true" />
        <span id="button-loading-text" className="sr-only">Loading...</span>
        {children}
      </>
    ) : (
      children
    )}
  </button>
);
```

### Keyboard Navigation

```typescript
const Modal = ({ isOpen, onClose, children }: ModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      // Trap focus within modal
      const focusableElements = modalRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      // Set focus to first focusable element
      (focusableElements?.[0] as HTMLElement)?.focus();
    }
  }, [isOpen]);

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      onKeyDown={handleKeyDown}
      className="modal"
    >
      {children}
    </div>
  );
};
```

## Maintenance Guidelines

### Component Updates

1. **Breaking Changes**: Follow semantic versioning for component APIs
2. **Deprecation Strategy**: Mark deprecated props with console warnings
3. **Migration Guides**: Provide clear migration paths for breaking changes
4. **Backward Compatibility**: Maintain compatibility for at least 2 major versions

### Code Quality Standards

1. **TypeScript**: All components must have complete type definitions
2. **Testing**: Minimum 80% test coverage for all components
3. **Documentation**: All public components must have Storybook stories
4. **Accessibility**: WCAG 2.1 AA compliance required
5. **Performance**: Components must pass performance budgets

### Review Process

1. **Design Review**: UX/UI team approval for new components
2. **Code Review**: Peer review with focus on reusability and performance
3. **Accessibility Review**: Automated and manual accessibility testing
4. **Testing Review**: Ensure adequate test coverage and scenarios

---

**Component Library Owner**: Frontend Engineering Team  
**Next Review**: 2025-12-29  
**Related Documents**: [Architecture Overview](./overview.md) | [Testing Guide](../../tests/)