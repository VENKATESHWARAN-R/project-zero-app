const axios = require('axios');
const logger = require('./logger');

class AuthService {
  constructor() {
    this.authServiceUrl =
      process.env.AUTH_SERVICE_URL || 'http://localhost:8001';
    this.timeout = parseInt(process.env.REQUEST_TIMEOUT || '5000');
  }

  async verifyToken(token) {
    try {
      logger.info('DEBUG: Verifying token with auth service', { 
        authServiceUrl: this.authServiceUrl, 
        tokenPreview: token.substring(0, 50) 
      });
      
      const response = await axios.get(`${this.authServiceUrl}/auth/verify`, {
        headers: {
          Authorization: `Bearer ${token}`
        },
        timeout: this.timeout,
      });

      if (response.status === 200 && response.data.valid) {
        return {
          valid: true,
          user_id: response.data.user_id,
          email: response.data.email,
        };
      }

      return { valid: false };
    } catch (error) {
      logger.error('DEBUG: Auth verification error', { 
        status: error.response?.status, 
        data: error.response?.data,
        message: error.message
      });
      
      if (error.response?.status === 401) {
        return { valid: false, error: 'Invalid token' };
      }

      if (error.code === 'ECONNREFUSED' || error.code === 'TIMEOUT') {
        throw new Error('Auth service unavailable');
      }

      throw new Error(`Auth service error: ${error.message}`);
    }
  }

  async checkHealth() {
    try {
      const response = await axios.get(`${this.authServiceUrl}/health`, {
        timeout: this.timeout,
      });
      return response.status === 200;
    } catch {
      return false;
    }
  }

  extractTokenFromHeader(authHeader) {
    if (!authHeader) {
      return null;
    }

    if (authHeader.startsWith('Bearer ')) {
      return authHeader.substring(7);
    }

    return null;
  }
}

module.exports = new AuthService();
