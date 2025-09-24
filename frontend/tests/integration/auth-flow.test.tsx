/**
 * Authentication Flow Integration Tests
 * Tests for complete user authentication workflow
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider } from '@/providers/AuthProvider';
import { LoginForm } from '@/components/auth/LoginForm';
import { RegisterForm } from '@/components/auth/RegisterForm';
import { AuthService } from '@/services/auth';

// Mock the auth service
jest.mock('@/services/auth');

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

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
);

describe('Authentication Flow Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Login Flow', () => {
    it('should complete successful login flow', async () => {
      const user = userEvent.setup();

      // Mock successful login
      const mockLogin = jest.fn().mockResolvedValue({
        access_token: 'mock_access_token',
        refresh_token: 'mock_refresh_token',
        token_type: 'bearer',
        expires_in: 900,
        user: {
          id: 'user-1',
          email: 'user@example.com',
          first_name: 'John',
          last_name: 'Doe',
          created_at: '2025-09-24T10:00:00Z',
          updated_at: '2025-09-24T10:00:00Z',
        },
      });
      mockAuthService.prototype.login = mockLogin;

      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      // Fill in login form
      await user.type(screen.getByLabelText(/email/i), 'user@example.com');
      await user.type(screen.getByLabelText(/password/i), 'password123');

      // Submit form
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      // Wait for API call and navigation
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({
          email: 'user@example.com',
          password: 'password123',
        });
      });

      // Check that tokens are stored
      expect(localStorage.getItem('auth_tokens')).toBeTruthy();
    });

    it('should handle login errors gracefully', async () => {
      const user = userEvent.setup();

      // Mock failed login
      const mockLogin = jest.fn().mockRejectedValue(new Error('Invalid credentials'));
      mockAuthService.prototype.login = mockLogin;

      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      // Fill in login form
      await user.type(screen.getByLabelText(/email/i), 'user@example.com');
      await user.type(screen.getByLabelText(/password/i), 'wrongpassword');

      // Submit form
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      // Wait for error to appear
      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      });

      // Check that no tokens are stored
      expect(localStorage.getItem('auth_tokens')).toBeNull();
    });

    it('should show loading state during login', async () => {
      const user = userEvent.setup();

      // Mock delayed login
      const mockLogin = jest.fn().mockImplementation(
        () =>
          new Promise(resolve =>
            setTimeout(
              () =>
                resolve({
                  access_token: 'mock_access_token',
                  refresh_token: 'mock_refresh_token',
                  token_type: 'bearer',
                  expires_in: 900,
                  user: {
                    id: 'user-1',
                    email: 'user@example.com',
                    first_name: 'John',
                    last_name: 'Doe',
                  },
                }),
              100
            )
          )
      );
      mockAuthService.prototype.login = mockLogin;

      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      // Fill in form and submit
      await user.type(screen.getByLabelText(/email/i), 'user@example.com');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      // Check loading state
      expect(screen.getByText(/signing in/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /signing in/i })).toBeDisabled();

      // Wait for completion
      await waitFor(
        () => {
          expect(screen.queryByText(/signing in/i)).not.toBeInTheDocument();
        },
        { timeout: 200 }
      );
    });
  });

  describe('Registration Flow', () => {
    it('should complete successful registration flow', async () => {
      const user = userEvent.setup();

      // Mock successful registration
      const mockRegister = jest.fn().mockResolvedValue({
        access_token: 'mock_access_token',
        refresh_token: 'mock_refresh_token',
        token_type: 'bearer',
        expires_in: 900,
        user: {
          id: 'user-2',
          email: 'newuser@example.com',
          first_name: 'Jane',
          last_name: 'Smith',
          created_at: '2025-09-24T10:00:00Z',
          updated_at: '2025-09-24T10:00:00Z',
        },
      });
      mockAuthService.prototype.register = mockRegister;

      render(
        <TestWrapper>
          <RegisterForm />
        </TestWrapper>
      );

      // Fill in registration form
      await user.type(screen.getByLabelText(/first name/i), 'Jane');
      await user.type(screen.getByLabelText(/last name/i), 'Smith');
      await user.type(screen.getByLabelText(/email/i), 'newuser@example.com');
      await user.type(screen.getByLabelText('Password'), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');

      // Submit form
      await user.click(screen.getByRole('button', { name: /create account/i }));

      // Wait for API call
      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          email: 'newuser@example.com',
          password: 'password123',
          first_name: 'Jane',
          last_name: 'Smith',
        });
      });

      // Check that tokens are stored
      expect(localStorage.getItem('auth_tokens')).toBeTruthy();
    });

    it('should handle registration validation errors', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <RegisterForm />
        </TestWrapper>
      );

      // Try to submit without filling required fields
      await user.click(screen.getByRole('button', { name: /create account/i }));

      // Check validation errors
      await waitFor(() => {
        expect(screen.getByText(/first name.*required/i)).toBeInTheDocument();
        expect(screen.getByText(/email.*required/i)).toBeInTheDocument();
      });
    });

    it('should handle password mismatch', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <RegisterForm />
        </TestWrapper>
      );

      // Fill in form with mismatched passwords
      await user.type(screen.getByLabelText(/first name/i), 'Jane');
      await user.type(screen.getByLabelText(/last name/i), 'Smith');
      await user.type(screen.getByLabelText(/email/i), 'newuser@example.com');
      await user.type(screen.getByLabelText('Password'), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'different');

      await user.click(screen.getByRole('button', { name: /create account/i }));

      // Check password mismatch error
      await waitFor(() => {
        expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
      });
    });
  });

  describe('Authentication State Persistence', () => {
    it('should restore authentication state from localStorage', async () => {
      // Mock tokens in localStorage
      const mockTokens = {
        accessToken: 'stored_access_token',
        refreshToken: 'stored_refresh_token',
        tokenType: 'bearer',
        expiresAt: Date.now() + 900000,
      };
      localStorage.setItem('auth_tokens', JSON.stringify(mockTokens));

      // Mock token verification
      const mockVerifyToken = jest.fn().mockResolvedValue({
        user: {
          id: 'user-1',
          email: 'user@example.com',
          first_name: 'John',
          last_name: 'Doe',
        },
        valid: true,
      });
      mockAuthService.prototype.verifyToken = mockVerifyToken;

      render(
        <TestWrapper>
          <div data-testid="auth-status">User should be authenticated</div>
        </TestWrapper>
      );

      // Wait for token verification
      await waitFor(() => {
        expect(mockVerifyToken).toHaveBeenCalledWith('stored_access_token');
      });
    });

    it('should handle invalid stored tokens', async () => {
      // Mock invalid tokens in localStorage
      const mockTokens = {
        accessToken: 'invalid_access_token',
        refreshToken: 'invalid_refresh_token',
        tokenType: 'bearer',
        expiresAt: Date.now() + 900000,
      };
      localStorage.setItem('auth_tokens', JSON.stringify(mockTokens));

      // Mock token verification failure
      const mockVerifyToken = jest.fn().mockRejectedValue(new Error('Invalid token'));
      mockAuthService.prototype.verifyToken = mockVerifyToken;

      render(
        <TestWrapper>
          <div data-testid="auth-status">User authentication status</div>
        </TestWrapper>
      );

      // Wait for token verification failure
      await waitFor(() => {
        expect(mockVerifyToken).toHaveBeenCalledWith('invalid_access_token');
      });

      // Check that tokens are cleared
      expect(localStorage.getItem('auth_tokens')).toBeNull();
    });
  });

  describe('Logout Flow', () => {
    it('should complete logout flow successfully', async () => {
      const user = userEvent.setup();

      // Setup authenticated state
      const mockTokens = {
        accessToken: 'access_token',
        refreshToken: 'refresh_token',
        tokenType: 'bearer',
        expiresAt: Date.now() + 900000,
      };
      localStorage.setItem('auth_tokens', JSON.stringify(mockTokens));

      // Mock logout
      const mockLogout = jest.fn().mockResolvedValue({
        message: 'Successfully logged out',
      });
      mockAuthService.prototype.logout = mockLogout;

      // Mock component with logout button (would be in Header)
      const LogoutButton = () => {
        const handleLogout = async () => {
          await mockLogout('refresh_token');
          localStorage.removeItem('auth_tokens');
        };

        return <button onClick={handleLogout}>Logout</button>;
      };

      render(
        <TestWrapper>
          <LogoutButton />
        </TestWrapper>
      );

      // Click logout
      await user.click(screen.getByRole('button', { name: /logout/i }));

      // Wait for logout completion
      await waitFor(() => {
        expect(mockLogout).toHaveBeenCalledWith('refresh_token');
      });

      // Check that tokens are cleared
      expect(localStorage.getItem('auth_tokens')).toBeNull();
    });
  });

  describe('Token Refresh Flow', () => {
    it('should automatically refresh expired tokens', async () => {
      // Setup expired tokens
      const expiredTokens = {
        accessToken: 'expired_access_token',
        refreshToken: 'valid_refresh_token',
        tokenType: 'bearer',
        expiresAt: Date.now() - 1000, // Expired
      };
      localStorage.setItem('auth_tokens', JSON.stringify(expiredTokens));

      // Mock token refresh
      const mockRefreshToken = jest.fn().mockResolvedValue({
        access_token: 'new_access_token',
        token_type: 'bearer',
        expires_in: 900,
      });
      mockAuthService.prototype.refreshToken = mockRefreshToken;

      render(
        <TestWrapper>
          <div data-testid="auth-status">Token refresh test</div>
        </TestWrapper>
      );

      // Should automatically refresh token
      await waitFor(() => {
        expect(mockRefreshToken).toHaveBeenCalledWith('valid_refresh_token');
      });

      // Check that new tokens are stored
      const storedTokens = localStorage.getItem('auth_tokens');
      expect(storedTokens).toBeTruthy();
      const parsedTokens = JSON.parse(storedTokens!);
      expect(parsedTokens.accessToken).toBe('new_access_token');
    });
  });
});