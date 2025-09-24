/**
 * Auth API Contract Tests
 * These tests verify that our auth service client correctly implements the API contract
 * Based on: /specs/004-build-a-next/contracts/auth-api.md
 */

import { AuthService } from '@/services/auth';

describe('Auth API Contract', () => {
  let authService: AuthService;

  beforeEach(() => {
    authService = new AuthService();
  });

  describe('POST /auth/login', () => {
    it('should authenticate user with valid credentials', async () => {
      const loginData = {
        email: 'user@example.com',
        password: 'securepassword123',
      };

      const response = await authService.login(loginData);

      expect(response).toMatchObject({
        access_token: expect.any(String),
        refresh_token: expect.any(String),
        token_type: 'bearer',
        expires_in: expect.any(Number),
        user: {
          id: expect.any(String),
          email: 'user@example.com',
          first_name: expect.any(String),
          last_name: expect.any(String),
          created_at: expect.any(String),
          updated_at: expect.any(String),
        },
      });
    });

    it('should handle invalid credentials with 401', async () => {
      const loginData = {
        email: 'user@example.com',
        password: 'wrongpassword',
      };

      await expect(authService.login(loginData)).rejects.toThrow('Invalid credentials');
    });
  });

  describe('POST /auth/register', () => {
    it('should register new user successfully', async () => {
      const registerData = {
        email: 'newuser@example.com',
        password: 'securepassword123',
        first_name: 'Jane',
        last_name: 'Smith',
      };

      const response = await authService.register(registerData);

      expect(response).toMatchObject({
        access_token: expect.any(String),
        refresh_token: expect.any(String),
        token_type: 'bearer',
        expires_in: expect.any(Number),
        user: {
          id: expect.any(String),
          email: 'newuser@example.com',
          first_name: 'Jane',
          last_name: 'Smith',
          created_at: expect.any(String),
          updated_at: expect.any(String),
        },
      });
    });

    it('should handle email already exists with 409', async () => {
      const registerData = {
        email: 'existing@example.com',
        password: 'securepassword123',
        first_name: 'Jane',
        last_name: 'Smith',
      };

      await expect(authService.register(registerData)).rejects.toThrow('Email already exists');
    });
  });

  describe('POST /auth/refresh', () => {
    it('should refresh access token with valid refresh token', async () => {
      const refreshToken = 'valid_refresh_token';

      const response = await authService.refreshToken(refreshToken);

      expect(response).toMatchObject({
        access_token: expect.any(String),
        token_type: 'bearer',
        expires_in: expect.any(Number),
      });
    });

    it('should handle invalid refresh token with 401', async () => {
      const invalidRefreshToken = 'invalid_token';

      await expect(authService.refreshToken(invalidRefreshToken)).rejects.toThrow(
        'Invalid or expired refresh token'
      );
    });
  });

  describe('POST /auth/logout', () => {
    it('should logout user successfully', async () => {
      const refreshToken = 'valid_refresh_token';

      const response = await authService.logout(refreshToken);

      expect(response).toMatchObject({
        message: 'Successfully logged out',
      });
    });
  });

  describe('GET /auth/verify', () => {
    it('should verify valid access token', async () => {
      const accessToken = 'valid_access_token';

      const response = await authService.verifyToken(accessToken);

      expect(response).toMatchObject({
        user: {
          id: expect.any(String),
          email: expect.any(String),
          first_name: expect.any(String),
          last_name: expect.any(String),
        },
        valid: true,
      });
    });

    it('should handle invalid access token with 401', async () => {
      const invalidToken = 'invalid_token';

      await expect(authService.verifyToken(invalidToken)).rejects.toThrow(
        'Invalid or expired token'
      );
    });
  });
});