const { UserNotificationPreference } = require('../models');

class PreferenceService {
  /**
   * Get user preferences with defaults
   */
  async getUserPreferences(userId) {
    try {
      return await UserNotificationPreference.getEffectivePreferences(userId);
    } catch (error) {
      console.error('Error getting user preferences:', error);
      throw error;
    }
  }

  /**
   * Update user preferences
   */
  async updateUserPreferences(userId, preferences) {
    try {
      // Validate preferences structure
      if (!Array.isArray(preferences)) {
        throw new Error('Preferences must be an array');
      }

      // Validate each preference
      const validTypes = ['welcome', 'order', 'payment', 'system', 'promotional'];
      const validChannels = ['email', 'sms', 'in_app'];
      const validFrequencies = ['immediate', 'daily', 'weekly', 'disabled'];

      const seenCombinations = new Set();

      for (const pref of preferences) {
        // Required fields validation
        if (!pref.type || !pref.channel || pref.enabled === undefined) {
          throw new Error('Each preference must have type, channel, and enabled fields');
        }

        // Type validation
        if (!validTypes.includes(pref.type)) {
          throw new Error(`Invalid notification type: ${pref.type}`);
        }

        // Channel validation
        if (!validChannels.includes(pref.channel)) {
          throw new Error(`Invalid notification channel: ${pref.channel}`);
        }

        // Frequency validation
        if (pref.frequency && !validFrequencies.includes(pref.frequency)) {
          throw new Error(`Invalid frequency: ${pref.frequency}`);
        }

        // Check for duplicates
        const combination = `${pref.type}_${pref.channel}`;
        if (seenCombinations.has(combination)) {
          throw new Error(`Duplicate preference for ${pref.type} via ${pref.channel}`);
        }
        seenCombinations.add(combination);

        // Auto-set frequency based on enabled status
        if (!pref.enabled && !pref.frequency) {
          pref.frequency = 'disabled';
        } else if (pref.enabled && (!pref.frequency || pref.frequency === 'disabled')) {
          pref.frequency = 'immediate';
        }
      }

      // Use transaction for consistency
      const { sequelize } = require('../config/database');
      const result = await sequelize.transaction(async(transaction) => {
        return await UserNotificationPreference.upsertPreferences(
          userId,
          preferences,
          transaction
        );
      });

      // Return effective preferences after update
      return await this.getUserPreferences(userId);
    } catch (error) {
      console.error('Error updating user preferences:', error);
      throw error;
    }
  }

  /**
   * Get preference for specific type and channel
   */
  async getUserPreference(userId, type, channel) {
    try {
      const preference = await UserNotificationPreference.findByUserTypeAndChannel(
        userId,
        type,
        channel
      );

      if (!preference) {
        // Return default preference
        const defaultEnabled = this.getDefaultPreference(type, channel);
        return {
          userId,
          type,
          channel,
          enabled: defaultEnabled,
          frequency: defaultEnabled ? 'immediate' : 'disabled',
          metadata: {},
        };
      }

      return preference;
    } catch (error) {
      console.error('Error getting user preference:', error);
      throw error;
    }
  }

  /**
   * Check if notification is allowed for user
   */
  async isNotificationAllowed(userId, type, channel) {
    try {
      return await UserNotificationPreference.isAllowed(userId, type, channel);
    } catch (error) {
      console.error('Error checking if notification is allowed:', error);
      throw error;
    }
  }

  /**
   * Enable all notifications for a user (opt-in)
   */
  async enableAllNotifications(userId) {
    try {
      const allPreferences = [
        { type: 'welcome', channel: 'email', enabled: true, frequency: 'immediate' },
        { type: 'order', channel: 'email', enabled: true, frequency: 'immediate' },
        { type: 'order', channel: 'sms', enabled: true, frequency: 'immediate' },
        { type: 'payment', channel: 'email', enabled: true, frequency: 'immediate' },
        { type: 'payment', channel: 'sms', enabled: true, frequency: 'immediate' },
        { type: 'system', channel: 'in_app', enabled: true, frequency: 'immediate' },
        { type: 'system', channel: 'email', enabled: true, frequency: 'immediate' },
        { type: 'promotional', channel: 'email', enabled: true, frequency: 'immediate' },
      ];

      return await this.updateUserPreferences(userId, allPreferences);
    } catch (error) {
      console.error('Error enabling all notifications:', error);
      throw error;
    }
  }

  /**
   * Disable promotional notifications (common GDPR requirement)
   */
  async disablePromotionalNotifications(userId) {
    try {
      const promotionalPreferences = [
        { type: 'promotional', channel: 'email', enabled: false, frequency: 'disabled' },
        { type: 'promotional', channel: 'sms', enabled: false, frequency: 'disabled' },
        { type: 'promotional', channel: 'in_app', enabled: false, frequency: 'disabled' },
      ];

      return await this.updateUserPreferences(userId, promotionalPreferences);
    } catch (error) {
      console.error('Error disabling promotional notifications:', error);
      throw error;
    }
  }

  /**
   * Set minimal notifications (only essential)
   */
  async setMinimalNotifications(userId) {
    try {
      const minimalPreferences = [
        { type: 'welcome', channel: 'email', enabled: false, frequency: 'disabled' },
        { type: 'order', channel: 'email', enabled: true, frequency: 'immediate' },
        { type: 'order', channel: 'sms', enabled: false, frequency: 'disabled' },
        { type: 'payment', channel: 'email', enabled: true, frequency: 'immediate' },
        { type: 'payment', channel: 'sms', enabled: false, frequency: 'disabled' },
        { type: 'system', channel: 'in_app', enabled: true, frequency: 'immediate' },
        { type: 'system', channel: 'email', enabled: false, frequency: 'disabled' },
        { type: 'promotional', channel: 'email', enabled: false, frequency: 'disabled' },
      ];

      return await this.updateUserPreferences(userId, minimalPreferences);
    } catch (error) {
      console.error('Error setting minimal notifications:', error);
      throw error;
    }
  }

  /**
   * Get default preference for type/channel combination
   */
  getDefaultPreference(type, channel) {
    const defaults = {
      'welcome_email': true,
      'order_email': true,
      'order_sms': false,
      'payment_email': true,
      'payment_sms': true,
      'system_in_app': true,
      'system_email': false,
      'promotional_email': false, // Opt-in required
      'promotional_sms': false,
      'promotional_in_app': false,
    };

    const key = `${type}_${channel}`;
    return defaults[key] || false;
  }

  /**
   * Get preferences summary for a user
   */
  async getPreferencesSummary(userId) {
    try {
      const preferences = await this.getUserPreferences(userId);

      const summary = {
        userId,
        totalPreferences: preferences.length,
        enabled: 0,
        disabled: 0,
        byType: {},
        byChannel: {},
        byFrequency: {},
      };

      preferences.forEach(pref => {
        if (pref.enabled) {
          summary.enabled++;
        } else {
          summary.disabled++;
        }

        // Count by type
        if (!summary.byType[pref.type]) {
          summary.byType[pref.type] = { enabled: 0, disabled: 0 };
        }
        summary.byType[pref.type][pref.enabled ? 'enabled' : 'disabled']++;

        // Count by channel
        if (!summary.byChannel[pref.channel]) {
          summary.byChannel[pref.channel] = { enabled: 0, disabled: 0 };
        }
        summary.byChannel[pref.channel][pref.enabled ? 'enabled' : 'disabled']++;

        // Count by frequency
        if (!summary.byFrequency[pref.frequency]) {
          summary.byFrequency[pref.frequency] = 0;
        }
        summary.byFrequency[pref.frequency]++;
      });

      return summary;
    } catch (error) {
      console.error('Error getting preferences summary:', error);
      throw error;
    }
  }

  /**
   * Reset user preferences to defaults
   */
  async resetToDefaults(userId) {
    try {
      // Delete all existing preferences for the user
      await UserNotificationPreference.destroy({
        where: { userId },
      });

      // Return effective preferences (which will be defaults)
      return await this.getUserPreferences(userId);
    } catch (error) {
      console.error('Error resetting preferences to defaults:', error);
      throw error;
    }
  }

  /**
   * Validate preference update request
   */
  validatePreferenceUpdate(preferences) {
    if (!Array.isArray(preferences)) {
      return { valid: false, error: 'Preferences must be an array' };
    }

    const validTypes = ['welcome', 'order', 'payment', 'system', 'promotional'];
    const validChannels = ['email', 'sms', 'in_app'];
    const validFrequencies = ['immediate', 'daily', 'weekly', 'disabled'];

    for (let i = 0; i < preferences.length; i++) {
      const pref = preferences[i];

      if (!pref.type || !pref.channel || pref.enabled === undefined) {
        return {
          valid: false,
          error: `Preference at index ${i} must have type, channel, and enabled fields`,
        };
      }

      if (!validTypes.includes(pref.type)) {
        return { valid: false, error: `Invalid type '${pref.type}' at index ${i}` };
      }

      if (!validChannels.includes(pref.channel)) {
        return { valid: false, error: `Invalid channel '${pref.channel}' at index ${i}` };
      }

      if (pref.frequency && !validFrequencies.includes(pref.frequency)) {
        return { valid: false, error: `Invalid frequency '${pref.frequency}' at index ${i}` };
      }
    }

    return { valid: true };
  }
}

module.exports = PreferenceService;