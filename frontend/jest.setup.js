import '@testing-library/jest-dom';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
      prefetch: jest.fn(),
    };
  },
  usePathname() {
    return '/';
  },
  useSearchParams() {
    return new URLSearchParams();
  },
}));

// Mock environment variables
process.env.NEXT_PUBLIC_AUTH_API_URL = 'http://localhost:8001';
process.env.NEXT_PUBLIC_PRODUCTS_API_URL = 'http://localhost:8004';
process.env.NEXT_PUBLIC_CART_API_URL = 'http://localhost:8007';