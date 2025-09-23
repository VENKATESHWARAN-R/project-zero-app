const axios = require('axios');

class AuthService {
  constructor() {
    this.authServiceUrl =
      process.env.AUTH_SERVICE_URL || 'http://localhost:8001';
    this.timeout = parseInt(process.env.REQUEST_TIMEOUT || '5000');
  }

  async verifyToken(token) {
    try {
      const response = await axios.get(`${this.authServiceUrl}/auth/verify`, {
        headers: {
          Authorization: token,
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
    } catch (error) {
      return false;
    }
  }

  extractTokenFromHeader(authHeader) {
    if (!authHeader) {
      return null;
    }

    if (authHeader.startsWith('Bearer ')) {
      return authHeader;
    }

    return null;
  }
}

module.exports = new AuthService();
