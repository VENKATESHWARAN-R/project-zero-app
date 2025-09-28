const fetch = require('node-fetch');
const config = require('../config');
const logger = require('../utils/logger');

class UserProfileService {
  constructor() {
    this.baseUrl = config.USER_PROFILE_SERVICE_URL || 'http://localhost:8002';
    this.timeout = 5000; // 5 seconds
  }

  async getUserProfile(userId, token) {
    try {
      const response = await fetch(`${this.baseUrl}/profile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        timeout: this.timeout
      });

      if (!response.ok) {
        if (response.status === 404) {
          logger.info('User profile not found', { userId });
          return null;
        }
        throw new Error(`Failed to get user profile: ${response.status} ${response.statusText}`);
      }

      const profile = await response.json();
      logger.info('User profile retrieved', { userId });

      return profile;
    } catch (error) {
      logger.logError(error, null, { operation: 'getUserProfile', userId });
      // Don't throw error, return null to allow graceful degradation
      return null;
    }
  }

  async getUserContactInfo(userId, token) {
    try {
      const profile = await this.getUserProfile(userId, token);

      if (!profile) {
        return {
          email: null,
          phone: null,
          preferredContact: 'email'
        };
      }

      return {
        email: profile.email || profile.contactEmail,
        phone: profile.phone || profile.phoneNumber,
        preferredContact: profile.preferredContactMethod || 'email',
        firstName: profile.firstName,
        lastName: profile.lastName,
        fullName: profile.fullName || `${profile.firstName || ''} ${profile.lastName || ''}`.trim()
      };
    } catch (error) {
      logger.logError(error, null, { operation: 'getUserContactInfo', userId });
      return {
        email: null,
        phone: null,
        preferredContact: 'email'
      };
    }
  }

  async updateNotificationPreferences(userId, preferences, token) {
    try {
      const response = await fetch(`${this.baseUrl}/profile/notification-preferences`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ preferences }),
        timeout: this.timeout
      });

      if (!response.ok) {
        throw new Error(`Failed to update notification preferences: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      logger.info('Notification preferences updated in user profile', { userId });

      return result;
    } catch (error) {
      logger.logError(error, null, { operation: 'updateNotificationPreferences', userId });
      // Don't throw error to allow local preference updates to succeed
      return null;
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
      logger.logError(error, null, { operation: 'checkHealth', service: 'user-profile' });
      return false;
    }
  }

  async getUserLanguagePreference(userId, token) {
    try {
      const profile = await this.getUserProfile(userId, token);

      return profile?.language || profile?.locale || 'en';
    } catch (error) {
      logger.logError(error, null, { operation: 'getUserLanguagePreference', userId });
      return 'en'; // Default to English
    }
  }

  async getUserTimezone(userId, token) {
    try {
      const profile = await this.getUserProfile(userId, token);

      return profile?.timezone || 'UTC';
    } catch (error) {
      logger.logError(error, null, { operation: 'getUserTimezone', userId });
      return 'UTC'; // Default to UTC
    }
  }
}

module.exports = new UserProfileService();