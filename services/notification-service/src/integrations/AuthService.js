const fetch = require('node-fetch');
const config = require('../config');
const logger = require('../utils/logger');

class AuthService {
  constructor() {
    this.baseUrl = config.AUTH_SERVICE_URL;
    this.timeout = 5000; // 5 seconds
  }

  async verifyToken(token) {
    try {
      const response = await fetch(`${this.baseUrl}/auth/verify`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        timeout: this.timeout
      });

      if (!response.ok) {
        throw new Error(`Token verification failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      logger.info('Token verified successfully', { userId: data.user_id || data.userId });

      return {
        userId: data.user_id || data.userId,
        email: data.email,
        isAdmin: data.is_admin || data.isAdmin || false,
        valid: true
      };
    } catch (error) {
      logger.logError(error, null, { operation: 'verifyToken' });
      throw new Error(`Auth service verification failed: ${error.message}`);
    }
  }

  async getUserInfo(userId, token) {
    try {
      const response = await fetch(`${this.baseUrl}/users/${userId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        timeout: this.timeout
      });

      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error(`Failed to get user info: ${response.status} ${response.statusText}`);
      }

      const userData = await response.json();
      logger.info('User info retrieved', { userId });

      return userData;
    } catch (error) {
      logger.logError(error, null, { operation: 'getUserInfo', userId });
      throw new Error(`Failed to get user info: ${error.message}`);
    }
  }

  async checkHealth() {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        timeout: this.timeout
      });

      return response.ok;
    } catch (error) {
      logger.logError(error, null, { operation: 'checkHealth' });
      return false;
    }
  }

  async refreshToken(refreshToken) {
    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
        timeout: this.timeout
      });

      if (!response.ok) {
        throw new Error(`Token refresh failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      logger.info('Token refreshed successfully');

      return {
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        expiresIn: data.expires_in
      };
    } catch (error) {
      logger.logError(error, null, { operation: 'refreshToken' });
      throw new Error(`Token refresh failed: ${error.message}`);
    }
  }
}

module.exports = new AuthService();