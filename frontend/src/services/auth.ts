/**
 * Authentication service client
 * Handles all authentication-related API calls
 */

import { authApi, handleApiCall } from '@/lib/api';
import {
  User,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  RefreshTokenResponse,
  LogoutResponse,
  VerifyTokenResponse,
  AuthTokens
} from '@/types/user';

export class AuthService {
  /**
   * Login user with email and password
   */
  static async login(credentials: LoginRequest): Promise<LoginResponse> {
    return handleApiCall(
      () => authApi.post<LoginResponse>('/auth/login', credentials),
      'login'
    );
  }

  /**
   * Register new user account
   */
  static async register(userData: RegisterRequest): Promise<RegisterResponse> {
    return handleApiCall(
      () => authApi.post<RegisterResponse>('/auth/register', userData),
      'register'
    );
  }

  /**
   * Refresh access token using refresh token
   */
  static async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    return handleApiCall(
      () => authApi.post<RefreshTokenResponse>('/auth/refresh', {
        refresh_token: refreshToken
      }),
      'refresh token'
    );
  }

  /**
   * Logout user and invalidate refresh token
   */
  static async logout(refreshToken: string): Promise<LogoutResponse> {
    return handleApiCall(
      () => authApi.post<LogoutResponse>('/auth/logout', {
        refresh_token: refreshToken
      }),
      'logout'
    );
  }

  /**
   * Verify access token validity
   */
  static async verifyToken(): Promise<VerifyTokenResponse> {
    return handleApiCall(
      () => authApi.get<VerifyTokenResponse>('/auth/verify'),
      'verify token'
    );
  }

  /**
   * Transform API response to User object
   */
  static transformApiUser(apiUser: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    created_at?: string;
    updated_at?: string;
  }): User {
    return {
      id: apiUser.id,
      email: apiUser.email,
      firstName: apiUser.first_name,
      lastName: apiUser.last_name,
      createdAt: apiUser.created_at || new Date().toISOString(),
      updatedAt: apiUser.updated_at || new Date().toISOString(),
    };
  }

  /**
   * Transform login/register response to auth tokens
   */
  static transformToAuthTokens(response: LoginResponse | RegisterResponse): AuthTokens {
    return {
      accessToken: response.access_token,
      refreshToken: response.refresh_token,
      tokenType: response.token_type,
      expiresAt: Date.now() + (response.expires_in * 1000),
    };
  }

  /**
   * Store tokens in localStorage
   */
  static storeTokens(tokens: AuthTokens): void {
    localStorage.setItem('auth_tokens', JSON.stringify(tokens));
  }

  /**
   * Get tokens from localStorage
   */
  static getStoredTokens(): AuthTokens | null {
    try {
      const tokens = localStorage.getItem('auth_tokens');
      if (!tokens) return null;

      const parsed = JSON.parse(tokens);

      // Check if token is expired
      if (parsed.expiresAt && Date.now() > parsed.expiresAt) {
        localStorage.removeItem('auth_tokens');
        return null;
      }

      return parsed;
    } catch (error) {
      console.error('Failed to parse stored tokens:', error);
      localStorage.removeItem('auth_tokens');
      return null;
    }
  }

  /**
   * Clear stored tokens
   */
  static clearTokens(): void {
    localStorage.removeItem('auth_tokens');
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated(): boolean {
    const tokens = this.getStoredTokens();
    return tokens !== null && tokens.accessToken !== '';
  }

  /**
   * Get current user from stored tokens
   */
  static getCurrentUser(): User | null {
    try {
      const userStr = localStorage.getItem('current_user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.error('Failed to parse current user:', error);
      localStorage.removeItem('current_user');
      return null;
    }
  }

  /**
   * Store current user
   */
  static storeCurrentUser(user: User): void {
    localStorage.setItem('current_user', JSON.stringify(user));
  }

  /**
   * Clear current user
   */
  static clearCurrentUser(): void {
    localStorage.removeItem('current_user');
  }
}

export default AuthService;