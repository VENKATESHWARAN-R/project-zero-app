/**
 * Authentication store using Zustand
 * Manages user authentication state and actions
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { User, LoginRequest, RegisterRequest, AuthTokens } from '@/types/user';
import { AuthService } from '@/services/auth';

interface AuthState {
  // State
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  isInitializing: boolean;

  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  verifyToken: () => Promise<void>;
  clearError: () => void;
  initialize: () => Promise<void>;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    user: null,
    tokens: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
    isInitializing: true,

    // Actions
    login: async (credentials: LoginRequest) => {
      set({ isLoading: true, error: null });

      try {
        const response = await AuthService.login(credentials);

        // Transform API response
        const user = AuthService.transformApiUser(response.user);
        const tokens = AuthService.transformToAuthTokens(response);

        // Store tokens and user
        AuthService.storeTokens(tokens);
        AuthService.storeCurrentUser(user);

        set({
          user,
          tokens,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      } catch (error: any) {
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
          isLoading: false,
          error: error.detail || error.message || 'Login failed',
        });
        throw error;
      }
    },

    register: async (userData: RegisterRequest) => {
      set({ isLoading: true, error: null });

      try {
        const response = await AuthService.register(userData);

        // Transform API response
        const user = AuthService.transformApiUser(response.user);
        const tokens = AuthService.transformToAuthTokens(response);

        // Store tokens and user
        AuthService.storeTokens(tokens);
        AuthService.storeCurrentUser(user);

        set({
          user,
          tokens,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      } catch (error: any) {
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
          isLoading: false,
          error: error.detail || error.message || 'Registration failed',
        });
        throw error;
      }
    },

    logout: async () => {
      set({ isLoading: true });

      try {
        const tokens = get().tokens;

        // Call logout API if we have a refresh token
        if (tokens?.refreshToken) {
          try {
            await AuthService.logout(tokens.refreshToken);
          } catch (error) {
            // Continue with logout even if API call fails
            console.error('Logout API call failed:', error);
          }
        }

        // Clear stored data
        AuthService.clearTokens();
        AuthService.clearCurrentUser();

        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      } catch (error: any) {
        // Even if logout fails, clear local state
        AuthService.clearTokens();
        AuthService.clearCurrentUser();

        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
          isLoading: false,
          error: error.detail || error.message || 'Logout failed',
        });
      }
    },

    refreshToken: async () => {
      const tokens = get().tokens;

      if (!tokens?.refreshToken) {
        throw new Error('No refresh token available');
      }

      try {
        const response = await AuthService.refreshToken(tokens.refreshToken);

        const newTokens: AuthTokens = {
          ...tokens,
          accessToken: response.access_token,
          expiresAt: Date.now() + (response.expires_in * 1000),
        };

        // Store updated tokens
        AuthService.storeTokens(newTokens);

        set({
          tokens: newTokens,
          error: null,
        });
      } catch (error: any) {
        // Refresh failed, logout user
        get().logout();
        throw error;
      }
    },

    verifyToken: async () => {
      const tokens = get().tokens;

      if (!tokens?.accessToken) {
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
        });
        return;
      }

      try {
        const response = await AuthService.verifyToken();

        if (response.valid) {
          const user = AuthService.transformApiUser(response.user);
          AuthService.storeCurrentUser(user);

          set({
            user,
            isAuthenticated: true,
            error: null,
          });
        } else {
          // Token is invalid, clear state
          get().logout();
        }
      } catch (error: any) {
        // Token verification failed, logout user
        get().logout();
        throw error;
      }
    },

    initialize: async () => {
      set({ isInitializing: true });

      try {
        // Load stored tokens and user
        const storedTokens = AuthService.getStoredTokens();
        const storedUser = AuthService.getCurrentUser();

        if (storedTokens && storedUser) {
          set({
            tokens: storedTokens,
            user: storedUser,
            isAuthenticated: true,
          });

          // Verify token is still valid
          try {
            await get().verifyToken();
          } catch (error) {
            // Token invalid, state will be cleared by verifyToken
            console.error('Token verification failed during initialization:', error);
          }
        } else {
          // No stored auth data
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
          });
        }
      } catch (error: any) {
        console.error('Auth initialization failed:', error);
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
          error: 'Failed to initialize authentication',
        });
      } finally {
        set({ isInitializing: false });
      }
    },

    clearError: () => {
      set({ error: null });
    },

    setLoading: (loading: boolean) => {
      set({ isLoading: loading });
    },
  }))
);

// Auto-refresh token when it's about to expire
if (typeof window !== 'undefined') {
  useAuthStore.subscribe(
    (state) => state.tokens,
    (tokens) => {
      if (tokens && tokens.expiresAt) {
        const timeUntilExpiry = tokens.expiresAt - Date.now();
        const refreshTime = Math.max(0, timeUntilExpiry - 60000); // Refresh 1 minute before expiry

        if (refreshTime > 0) {
          setTimeout(async () => {
            const store = useAuthStore.getState();
            if (store.isAuthenticated && store.tokens) {
              try {
                await store.refreshToken();
              } catch (error) {
                console.error('Auto token refresh failed:', error);
              }
            }
          }, refreshTime);
        }
      }
    }
  );
}

export default useAuthStore;