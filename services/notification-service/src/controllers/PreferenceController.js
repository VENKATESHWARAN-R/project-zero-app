const PreferenceService = require('../services/PreferenceService');

// Create service instance
const preferenceService = new PreferenceService();

class PreferenceController {
  static async getPreferences(req, res) {
    try {
      const userId = req.user.userId;

      const preferences = await preferenceService.getUserPreferences(userId);

      res.status(200).json({
        userId,
        preferences
      });
    } catch (error) {
      console.error('Error getting preferences:', error);
      res.status(500).json({
        error: 'internal_error',
        message: 'Failed to retrieve preferences',
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }
  }

  static async updatePreferences(req, res) {
    try {
      const userId = req.user.userId;
      const { preferences } = req.body;

      if (!preferences || !Array.isArray(preferences)) {
        return res.status(400).json({
          error: 'validation_error',
          message: 'Preferences must be an array',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      // Validate preference format
      for (const pref of preferences) {
        if (!pref.type || !pref.channel || typeof pref.enabled !== 'boolean') {
          return res.status(400).json({
            error: 'validation_error',
            message: 'Each preference must have type, channel, and enabled fields',
            timestamp: new Date().toISOString(),
            path: req.path
          });
        }

        // Validate enum values
        const validTypes = ['welcome', 'order', 'payment', 'system', 'promotional'];
        const validChannels = ['email', 'sms', 'in_app'];
        const validFrequencies = ['immediate', 'daily', 'weekly', 'disabled'];

        if (!validTypes.includes(pref.type)) {
          return res.status(400).json({
            error: 'validation_error',
            message: `Invalid preference type: ${pref.type}. Must be one of: ${validTypes.join(', ')}`,
            timestamp: new Date().toISOString(),
            path: req.path
          });
        }

        if (!validChannels.includes(pref.channel)) {
          return res.status(400).json({
            error: 'validation_error',
            message: `Invalid channel: ${pref.channel}. Must be one of: ${validChannels.join(', ')}`,
            timestamp: new Date().toISOString(),
            path: req.path
          });
        }

        if (pref.frequency && !validFrequencies.includes(pref.frequency)) {
          return res.status(400).json({
            error: 'validation_error',
            message: `Invalid frequency: ${pref.frequency}. Must be one of: ${validFrequencies.join(', ')}`,
            timestamp: new Date().toISOString(),
            path: req.path
          });
        }

        // System notifications cannot be completely disabled
        if (pref.type === 'system' && !pref.enabled && pref.channel === 'in_app') {
          return res.status(400).json({
            error: 'validation_error',
            message: 'System in-app notifications cannot be disabled',
            timestamp: new Date().toISOString(),
            path: req.path
          });
        }
      }

      const updatedPreferences = await preferenceService.updateUserPreferences(userId, preferences);

      res.status(200).json({
        userId,
        preferences: updatedPreferences
      });
    } catch (error) {
      console.error('Error updating preferences:', error);
      res.status(500).json({
        error: 'internal_error',
        message: 'Failed to update preferences',
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }
  }
}

module.exports = PreferenceController;