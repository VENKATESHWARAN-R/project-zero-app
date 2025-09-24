/**
 * Header Component Tests
 * Tests for the main navigation header component
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { Header } from '@/components/layout/Header';
import { useAuthStore } from '@/store/auth';
import { useCartStore } from '@/store/cart';

// Mock the stores
jest.mock('@/store/auth');
jest.mock('@/store/cart');

const mockUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;
const mockUseCartStore = useCartStore as jest.MockedFunction<typeof useCartStore>;

const mockAuthenticatedUser = {
  id: 'user-1',
  email: 'user@example.com',
  firstName: 'John',
  lastName: 'Doe',
  createdAt: '2025-09-24T10:00:00Z',
  updatedAt: '2025-09-24T10:00:00Z',
};

describe('Header', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render logo and navigation links', () => {
    mockUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      logout: jest.fn(),
    } as any);

    mockUseCartStore.mockReturnValue({
      itemCount: 0,
    } as any);

    render(<Header />);

    expect(screen.getByText('Project Zero Store')).toBeInTheDocument();
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Products')).toBeInTheDocument();
    expect(screen.getByText('Login')).toBeInTheDocument();
    expect(screen.getByText('Register')).toBeInTheDocument();
  });

  it('should show cart icon with item count', () => {
    mockUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      logout: jest.fn(),
    } as any);

    mockUseCartStore.mockReturnValue({
      itemCount: 3,
    } as any);

    render(<Header />);

    expect(screen.getByLabelText('Cart')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('should show authenticated user menu', () => {
    mockUseAuthStore.mockReturnValue({
      user: mockAuthenticatedUser,
      isAuthenticated: true,
      logout: jest.fn(),
    } as any);

    mockUseCartStore.mockReturnValue({
      itemCount: 0,
    } as any);

    render(<Header />);

    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.queryByText('Login')).not.toBeInTheDocument();
    expect(screen.queryByText('Register')).not.toBeInTheDocument();
  });

  it('should show user dropdown menu on click', () => {
    const mockLogout = jest.fn();

    mockUseAuthStore.mockReturnValue({
      user: mockAuthenticatedUser,
      isAuthenticated: true,
      logout: mockLogout,
    } as any);

    mockUseCartStore.mockReturnValue({
      itemCount: 0,
    } as any);

    render(<Header />);

    fireEvent.click(screen.getByText('John'));

    expect(screen.getByText('Profile')).toBeInTheDocument();
    expect(screen.getByText('Cart')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });

  it('should handle logout click', () => {
    const mockLogout = jest.fn();

    mockUseAuthStore.mockReturnValue({
      user: mockAuthenticatedUser,
      isAuthenticated: true,
      logout: mockLogout,
    } as any);

    mockUseCartStore.mockReturnValue({
      itemCount: 0,
    } as any);

    render(<Header />);

    fireEvent.click(screen.getByText('John'));
    fireEvent.click(screen.getByText('Logout'));

    expect(mockLogout).toHaveBeenCalled();
  });

  it('should show mobile menu toggle on small screens', () => {
    // Mock window.innerWidth for mobile
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 768,
    });

    mockUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      logout: jest.fn(),
    } as any);

    mockUseCartStore.mockReturnValue({
      itemCount: 0,
    } as any);

    render(<Header />);

    expect(screen.getByLabelText('Toggle mobile menu')).toBeInTheDocument();
  });

  it('should toggle mobile menu visibility', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 768,
    });

    mockUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      logout: jest.fn(),
    } as any);

    mockUseCartStore.mockReturnValue({
      itemCount: 0,
    } as any);

    render(<Header />);

    const mobileMenuToggle = screen.getByLabelText('Toggle mobile menu');
    fireEvent.click(mobileMenuToggle);

    expect(screen.getByTestId('mobile-menu')).toHaveClass('mobile-menu-open');

    fireEvent.click(mobileMenuToggle);
    expect(screen.getByTestId('mobile-menu')).not.toHaveClass('mobile-menu-open');
  });

  it('should navigate to cart page on cart icon click', () => {
    const mockPush = jest.fn();
    jest.doMock('next/navigation', () => ({
      useRouter: () => ({ push: mockPush }),
    }));

    mockUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      logout: jest.fn(),
    } as any);

    mockUseCartStore.mockReturnValue({
      itemCount: 2,
    } as any);

    render(<Header />);

    fireEvent.click(screen.getByLabelText('Cart'));
    expect(mockPush).toHaveBeenCalledWith('/cart');
  });

  it('should show search bar on desktop', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    });

    mockUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      logout: jest.fn(),
    } as any);

    mockUseCartStore.mockReturnValue({
      itemCount: 0,
    } as any);

    render(<Header />);

    expect(screen.getByPlaceholderText('Search products...')).toBeInTheDocument();
  });
});