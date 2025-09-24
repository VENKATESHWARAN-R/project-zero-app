/**
 * Auth Store Tests
 * Tests for the authentication Zustand store
 */

import { act, renderHook } from '@testing-library/react';
import { useAuthStore } from '@/store/auth';
import { AuthService } from '@/services/auth';

// Mock the auth service
jest.mock('@/services/auth');

const mockAuthService = AuthService as jest.MockedClass<typeof AuthService>;

const mockLoginResponse = {
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
};

const mockRegisterResponse = {
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
};

describe('Auth Store', () => {
  beforeEach(() => {
    // Reset store state
    useAuthStore.setState({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });

    // Clear localStorage
    localStorage.clear();

    // Reset mocks
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useAuthStore());

      expect(result.current.user).toBeNull();
      expect(result.current.tokens).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });

  describe('Login', () => {
    it('should handle successful login', async () => {
      const mockLogin = jest.fn().mockResolvedValue(mockLoginResponse);
      mockAuthService.prototype.login = mockLogin;

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login('user@example.com', 'password123');
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).toEqual({
        id: 'user-1',
        email: 'user@example.com',
        firstName: 'John',
        lastName: 'Doe',
        createdAt: '2025-09-24T10:00:00Z',
        updatedAt: '2025-09-24T10:00:00Z',
      });
      expect(result.current.tokens).toEqual({
        accessToken: 'mock_access_token',
        refreshToken: 'mock_refresh_token',
        tokenType: 'bearer',
        expiresAt: expect.any(Number),
      });
      expect(result.current.error).toBeNull();
    });

    it('should handle login failure', async () => {
      const mockLogin = jest.fn().mockRejectedValue(new Error('Invalid credentials'));
      mockAuthService.prototype.login = mockLogin;

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login('user@example.com', 'wrongpassword');
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.tokens).toBeNull();
      expect(result.current.error).toBe('Invalid credentials');
    });

    it('should set loading state during login', async () => {
      const mockLogin = jest.fn().mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockLoginResponse), 100))
      );
      mockAuthService.prototype.login = mockLogin;

      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.login('user@example.com', 'password123');
      });

      expect(result.current.isLoading).toBe(true);

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 150));
      });

      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('Register', () => {
    it('should handle successful registration', async () => {
      const mockRegister = jest.fn().mockResolvedValue(mockRegisterResponse);
      mockAuthService.prototype.register = mockRegister;

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.register({
          email: 'newuser@example.com',
          password: 'password123',
          firstName: 'Jane',
          lastName: 'Smith',
        });
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).toEqual({
        id: 'user-2',
        email: 'newuser@example.com',
        firstName: 'Jane',
        lastName: 'Smith',
        createdAt: '2025-09-24T10:00:00Z',
        updatedAt: '2025-09-24T10:00:00Z',
      });
    });

    it('should handle registration failure', async () => {
      const mockRegister = jest.fn().mockRejectedValue(new Error('Email already exists'));
      mockAuthService.prototype.register = mockRegister;

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.register({
          email: 'existing@example.com',
          password: 'password123',
          firstName: 'Jane',
          lastName: 'Smith',
        });
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.error).toBe('Email already exists');
    });
  });

  describe('Token Refresh', () => {
    it('should refresh tokens successfully', async () => {
      const mockRefreshToken = jest.fn().mockResolvedValue({
        access_token: 'new_access_token',
        token_type: 'bearer',
        expires_in: 900,
      });
      mockAuthService.prototype.refreshToken = mockRefreshToken;

      const { result } = renderHook(() => useAuthStore());

      // Set initial tokens
      act(() => {
        useAuthStore.setState({
          tokens: {
            accessToken: 'old_access_token',
            refreshToken: 'refresh_token',
            tokenType: 'bearer',
            expiresAt: Date.now() - 1000, // Expired
          },
        });
      });

      await act(async () => {
        await result.current.refreshToken();
      });

      expect(result.current.tokens?.accessToken).toBe('new_access_token');
      expect(mockRefreshToken).toHaveBeenCalledWith('refresh_token');
    });

    it('should handle refresh failure and logout', async () => {
      const mockRefreshToken = jest.fn().mockRejectedValue(new Error('Invalid refresh token'));
      mockAuthService.prototype.refreshToken = mockRefreshToken;

      const { result } = renderHook(() => useAuthStore());

      // Set initial authenticated state
      act(() => {
        useAuthStore.setState({
          user: mockLoginResponse.user,
          tokens: {
            accessToken: 'access_token',
            refreshToken: 'refresh_token',
            tokenType: 'bearer',
            expiresAt: Date.now() - 1000,
          },
          isAuthenticated: true,
        });
      });

      await act(async () => {
        await result.current.refreshToken();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.tokens).toBeNull();
    });
  });

  describe('Logout', () => {
    it('should clear user data and tokens on logout', async () => {
      const mockLogout = jest.fn().mockResolvedValue({ message: 'Successfully logged out' });
      mockAuthService.prototype.logout = mockLogout;

      const { result } = renderHook(() => useAuthStore());

      // Set authenticated state
      act(() => {
        useAuthStore.setState({
          user: mockLoginResponse.user,
          tokens: {
            accessToken: 'access_token',
            refreshToken: 'refresh_token',
            tokenType: 'bearer',
            expiresAt: Date.now() + 900000,
          },
          isAuthenticated: true,
        });
      });

      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.tokens).toBeNull();
      expect(mockLogout).toHaveBeenCalledWith('refresh_token');
    });
  });

  describe('Error Handling', () => {
    it('should clear error', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        useAuthStore.setState({ error: 'Some error' });
      });

      expect(result.current.error).toBe('Some error');

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('Persistence', () => {
    it('should save tokens to localStorage on login', async () => {
      const mockLogin = jest.fn().mockResolvedValue(mockLoginResponse);
      mockAuthService.prototype.login = mockLogin;

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login('user@example.com', 'password123');
      });

      const savedTokens = localStorage.getItem('auth_tokens');
      expect(savedTokens).toBeTruthy();

      const parsedTokens = JSON.parse(savedTokens!);
      expect(parsedTokens.accessToken).toBe('mock_access_token');
      expect(parsedTokens.refreshToken).toBe('mock_refresh_token');
    });

    it('should remove tokens from localStorage on logout', async () => {
      const mockLogout = jest.fn().mockResolvedValue({ message: 'Successfully logged out' });
      mockAuthService.prototype.logout = mockLogout;

      // Set initial tokens in localStorage
      localStorage.setItem(
        'auth_tokens',
        JSON.stringify({
          accessToken: 'access_token',
          refreshToken: 'refresh_token',
          tokenType: 'bearer',
          expiresAt: Date.now() + 900000,
        })
      );

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.logout();
      });

      expect(localStorage.getItem('auth_tokens')).toBeNull();
    });
  });
});