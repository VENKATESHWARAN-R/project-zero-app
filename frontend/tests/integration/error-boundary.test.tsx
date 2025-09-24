/**
 * Error Boundary and Fallback Integration Tests
 * Tests for error handling and recovery mechanisms
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { ProductsService } from '@/services/products';
import { CartService } from '@/services/cart';
import { AuthService } from '@/services/auth';

// Mock services to throw errors
jest.mock('@/services/products');
jest.mock('@/services/cart');
jest.mock('@/services/auth');

const mockProductsService = ProductsService as jest.MockedClass<typeof ProductsService>;
const mockCartService = CartService as jest.MockedClass<typeof CartService>;
const mockAuthService = AuthService as jest.MockedClass<typeof AuthService>;

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
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
}));

// Component that throws an error for testing
const ThrowError = ({ shouldThrow = false }: { shouldThrow?: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>Component rendered successfully</div>;
};

// Component that makes API calls
const APIComponent = ({
  action,
  shouldFail = false
}: {
  action: 'products' | 'cart' | 'auth';
  shouldFail?: boolean;
}) => {
  const [data, setData] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        let result;

        if (shouldFail) {
          throw new Error(`${action} API failed`);
        }

        switch (action) {
          case 'products':
            result = await new ProductsService().getProducts();
            break;
          case 'cart':
            result = await new CartService().getCart();
            break;
          case 'auth':
            result = await new AuthService().verifyToken('test-token');
            break;
          default:
            result = null;
        }

        setData(result);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [action, shouldFail]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (data) return <div>Data loaded successfully</div>;

  return null;
};

describe('Error Boundary and Fallback Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    (console.error as jest.Mock).mockRestore();
  });

  describe('Error Boundary', () => {
    it('should catch and display JavaScript errors', () => {
      render(
        <ErrorBoundary fallback={<div>Something went wrong</div>}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.queryByText('Component rendered successfully')).not.toBeInTheDocument();
    });

    it('should render children when no errors occur', () => {
      render(
        <ErrorBoundary fallback={<div>Something went wrong</div>}>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Component rendered successfully')).toBeInTheDocument();
      expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
    });

    it('should provide error details in fallback', () => {
      const ErrorFallback = ({ error }: { error?: Error }) => (
        <div>
          <h2>Error occurred</h2>
          <p>Message: {error?.message}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      );

      render(
        <ErrorBoundary fallback={(error) => <ErrorFallback error={error} />}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Error occurred')).toBeInTheDocument();
      expect(screen.getByText('Message: Test error')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });

    it('should isolate errors to specific components', () => {
      render(
        <div>
          <ErrorBoundary fallback={<div>Error in component 1</div>}>
            <ThrowError shouldThrow={true} />
          </ErrorBoundary>
          <ErrorBoundary fallback={<div>Error in component 2</div>}>
            <ThrowError shouldThrow={false} />
          </ErrorBoundary>
        </div>
      );

      expect(screen.getByText('Error in component 1')).toBeInTheDocument();
      expect(screen.getByText('Component rendered successfully')).toBeInTheDocument();
      expect(screen.queryByText('Error in component 2')).not.toBeInTheDocument();
    });
  });

  describe('API Error Handling', () => {
    it('should handle products API failures gracefully', async () => {
      mockProductsService.prototype.getProducts = jest.fn().mockRejectedValue(
        new Error('products API failed')
      );

      render(
        <ErrorBoundary fallback={<div>Products error boundary</div>}>
          <APIComponent action="products" shouldFail={true} />
        </ErrorBoundary>
      );

      await waitFor(() => {
        expect(screen.getByText('Error: products API failed')).toBeInTheDocument();
      });

      // Error boundary should not catch API errors (they're handled in component)
      expect(screen.queryByText('Products error boundary')).not.toBeInTheDocument();
    });

    it('should handle cart API failures gracefully', async () => {
      mockCartService.prototype.getCart = jest.fn().mockRejectedValue(
        new Error('cart API failed')
      );

      render(
        <ErrorBoundary fallback={<div>Cart error boundary</div>}>
          <APIComponent action="cart" shouldFail={true} />
        </ErrorBoundary>
      );

      await waitFor(() => {
        expect(screen.getByText('Error: cart API failed')).toBeInTheDocument();
      });

      expect(screen.queryByText('Cart error boundary')).not.toBeInTheDocument();
    });

    it('should handle auth API failures gracefully', async () => {
      mockAuthService.prototype.verifyToken = jest.fn().mockRejectedValue(
        new Error('auth API failed')
      );

      render(
        <ErrorBoundary fallback={<div>Auth error boundary</div>}>
          <APIComponent action="auth" shouldFail={true} />
        </ErrorBoundary>
      );

      await waitFor(() => {
        expect(screen.getByText('Error: auth API failed')).toBeInTheDocument();
      });

      expect(screen.queryByText('Auth error boundary')).not.toBeInTheDocument();
    });
  });

  describe('Network Error Recovery', () => {
    it('should handle network errors with retry mechanism', async () => {
      const user = userEvent.setup();

      // First call fails, second succeeds
      mockProductsService.prototype.getProducts = jest.fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({ products: [], pagination: {} });

      const RetryComponent = () => {
        const [retryCount, setRetryCount] = React.useState(0);

        return (
          <div>
            <APIComponent
              action="products"
              shouldFail={retryCount === 0}
            />
            <button onClick={() => setRetryCount(prev => prev + 1)}>
              Retry
            </button>
          </div>
        );
      };

      render(<RetryComponent />);

      // Should show error initially
      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });

      // Click retry button
      await user.click(screen.getByRole('button', { name: /retry/i }));

      // Should show success after retry
      await waitFor(() => {
        expect(screen.getByText('Data loaded successfully')).toBeInTheDocument();
      });
    });

    it('should handle offline state gracefully', () => {
      // Mock navigator.onLine
      Object.defineProperty(navigator, 'onLine', {
        writable: true,
        value: false,
      });

      const OfflineIndicator = () => {
        const [isOnline, setIsOnline] = React.useState(navigator.onLine);

        React.useEffect(() => {
          const handleOnline = () => setIsOnline(true);
          const handleOffline = () => setIsOnline(false);

          window.addEventListener('online', handleOnline);
          window.addEventListener('offline', handleOffline);

          return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
          };
        }, []);

        return (
          <div>
            {isOnline ? (
              <span>Online</span>
            ) : (
              <div>
                <span>Offline</span>
                <p>Please check your internet connection</p>
              </div>
            )}
          </div>
        );
      };

      render(<OfflineIndicator />);

      expect(screen.getByText('Offline')).toBeInTheDocument();
      expect(screen.getByText('Please check your internet connection')).toBeInTheDocument();
    });
  });

  describe('Graceful Degradation', () => {
    it('should show loading states during API calls', async () => {
      // Mock delayed API response
      mockProductsService.prototype.getProducts = jest.fn().mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      );

      render(<APIComponent action="products" />);

      // Should show loading state
      expect(screen.getByText('Loading...')).toBeInTheDocument();

      // Wait for completion
      await waitFor(
        () => {
          expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
        },
        { timeout: 200 }
      );
    });

    it('should handle missing data gracefully', () => {
      const SafeComponent = ({ data }: { data?: any }) => {
        return (
          <div>
            <h1>{data?.title || 'Default Title'}</h1>
            <p>{data?.description || 'No description available'}</p>
            {data?.items?.length ? (
              <ul>
                {data.items.map((item: any, index: number) => (
                  <li key={index}>{item.name}</li>
                ))}
              </ul>
            ) : (
              <p>No items to display</p>
            )}
          </div>
        );
      };

      render(<SafeComponent data={null} />);

      expect(screen.getByText('Default Title')).toBeInTheDocument();
      expect(screen.getByText('No description available')).toBeInTheDocument();
      expect(screen.getByText('No items to display')).toBeInTheDocument();
    });

    it('should provide fallback UI for failed image loads', () => {
      const ImageWithFallback = ({ src, alt }: { src: string; alt: string }) => {
        const [hasError, setHasError] = React.useState(false);

        return hasError ? (
          <div className="image-fallback">
            <span>Image not available</span>
          </div>
        ) : (
          <img
            src={src}
            alt={alt}
            onError={() => setHasError(true)}
          />
        );
      };

      render(<ImageWithFallback src="invalid-url.jpg" alt="Test image" />);

      // Trigger image error
      const img = screen.getByRole('img');
      fireEvent.error(img);

      expect(screen.getByText('Image not available')).toBeInTheDocument();
    });
  });

  describe('Error Logging and Reporting', () => {
    it('should log errors for debugging', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary
          fallback={<div>Error occurred</div>}
          onError={(error) => console.error('Caught error:', error.message)}
        >
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(consoleSpy).toHaveBeenCalledWith('Caught error:', 'Test error');
    });

    it('should provide error context for reporting', () => {
      const errorReportSpy = jest.fn();

      const ErrorBoundaryWithReporting = ({ children }: { children: React.ReactNode }) => {
        return (
          <ErrorBoundary
            fallback={<div>Error reported</div>}
            onError={(error, errorInfo) => {
              errorReportSpy({
                message: error.message,
                stack: error.stack,
                componentStack: errorInfo?.componentStack,
                timestamp: new Date().toISOString(),
              });
            }}
          >
            {children}
          </ErrorBoundary>
        );
      };

      render(
        <ErrorBoundaryWithReporting>
          <ThrowError shouldThrow={true} />
        </ErrorBoundaryWithReporting>
      );

      expect(errorReportSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Test error',
          stack: expect.any(String),
          timestamp: expect.any(String),
        })
      );
    });
  });
});