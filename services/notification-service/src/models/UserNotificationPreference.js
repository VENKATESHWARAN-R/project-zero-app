const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const UserNotificationPreference = sequelize.define('UserNotificationPreference', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  userId: {
    type: DataTypes.STRING(255),
    allowNull: false,
    validate: {
      notEmpty: true,
    },
  },
  type: {
    type: DataTypes.ENUM('welcome', 'order', 'payment', 'system', 'promotional'),
    allowNull: false,
    validate: {
      isIn: [['welcome', 'order', 'payment', 'system', 'promotional']],
    },
  },
  channel: {
    type: DataTypes.ENUM('email', 'sms', 'in_app'),
    allowNull: false,
    validate: {
      isIn: [['email', 'sms', 'in_app']],
    },
  },
  enabled: {
    type: DataTypes.BOOLEAN,
    allowNull: false,
    defaultValue: true,
  },
  frequency: {
    type: DataTypes.ENUM('immediate', 'daily', 'weekly', 'disabled'),
    allowNull: false,
    defaultValue: 'immediate',
    validate: {
      isIn: [['immediate', 'daily', 'weekly', 'disabled']],
      isConsistentWithEnabled(value) {
        if (!this.enabled && value !== 'disabled') {
          throw new Error('Frequency must be disabled when preference is disabled');
        }
        if (this.enabled && value === 'disabled') {
          throw new Error('Frequency cannot be disabled when preference is enabled');
        }
      },
    },
  },
  metadata: {
    type: DataTypes.JSON,
    allowNull: true,
    defaultValue: {},
  },
}, {
  tableName: 'user_notification_preferences',
  indexes: [
    {
      fields: ['userId'],
      name: 'idx_user_notification_preferences_user_id',
    },
    {
      fields: ['type', 'channel'],
      name: 'idx_user_notification_preferences_type_channel',
    },
    {
      fields: ['userId', 'type', 'channel'],
      unique: true,
      name: 'unique_user_type_channel',
    },
  ],
  validate: {
    systemNotificationsMinimum() {
      // System notifications must have at least in-app enabled
      if (this.type === 'system' && this.channel === 'in_app' && !this.enabled) {
        throw new Error('System in-app notifications cannot be completely disabled');
      }
    },
  },
  hooks: {
    beforeSave: async(preference, options) => {
      // Auto-correct frequency based on enabled status
      if (!preference.enabled) {
        preference.frequency = 'disabled';
      } else if (preference.frequency === 'disabled') {
        preference.frequency = 'immediate';
      }
    },
  },
});

// Class methods
UserNotificationPreference.findByUser = function(userId, options = {}) {
  return this.findAll({
    where: { userId },
    order: [['type', 'ASC'], ['channel', 'ASC']],
    ...options,
  });
};

UserNotificationPreference.findByUserAndType = function(userId, type, options = {}) {
  return this.findAll({
    where: { userId, type },
    order: [['channel', 'ASC']],
    ...options,
  });
};

UserNotificationPreference.findByUserTypeAndChannel = function(userId, type, channel) {
  return this.findOne({
    where: { userId, type, channel },
  });
};

UserNotificationPreference.isAllowed = async function(userId, type, channel) {
  const preference = await this.findByUserTypeAndChannel(userId, type, channel);

  if (!preference) {
    // Default behavior: allow system and order notifications, require opt-in for promotional
    if (type === 'promotional') {
      return false; // Promotional requires explicit opt-in
    }
    return true; // Allow by default for other types
  }

  return preference.enabled && preference.frequency !== 'disabled';
};

UserNotificationPreference.getEffectivePreferences = async function(userId) {
  const preferences = await this.findByUser(userId);

  // Create a map of preferences
  const prefMap = new Map();
  preferences.forEach(pref => {
    const key = `${pref.type}_${pref.channel}`;
    prefMap.set(key, pref);
  });

  // Define default preferences
  const defaultPreferences = [
    { type: 'welcome', channel: 'email', enabled: true, frequency: 'immediate' },
    { type: 'order', channel: 'email', enabled: true, frequency: 'immediate' },
    { type: 'order', channel: 'sms', enabled: false, frequency: 'disabled' },
    { type: 'payment', channel: 'email', enabled: true, frequency: 'immediate' },
    { type: 'payment', channel: 'sms', enabled: true, frequency: 'immediate' },
    { type: 'system', channel: 'in_app', enabled: true, frequency: 'immediate' },
    { type: 'system', channel: 'email', enabled: false, frequency: 'disabled' },
    { type: 'promotional', channel: 'email', enabled: false, frequency: 'disabled' },
  ];

  // Merge defaults with user preferences
  const effectivePreferences = defaultPreferences.map(defaultPref => {
    const key = `${defaultPref.type}_${defaultPref.channel}`;
    const userPref = prefMap.get(key);

    if (userPref) {
      return {
        id: userPref.id,
        userId: userPref.userId,
        type: userPref.type,
        channel: userPref.channel,
        enabled: userPref.enabled,
        frequency: userPref.frequency,
        metadata: userPref.metadata,
        createdAt: userPref.createdAt,
        updatedAt: userPref.updatedAt,
      };
    } else {
      return {
        userId,
        ...defaultPref,
        metadata: {},
      };
    }
  });

  return effectivePreferences;
};

UserNotificationPreference.upsertPreferences = async function(userId, preferences, transaction = null) {
  const results = [];

  for (const pref of preferences) {
    const [preference, created] = await this.findOrCreate({
      where: {
        userId,
        type: pref.type,
        channel: pref.channel,
      },
      defaults: {
        userId,
        type: pref.type,
        channel: pref.channel,
        enabled: pref.enabled,
        frequency: pref.frequency,
        metadata: pref.metadata || {},
      },
      transaction,
    });

    if (!created) {
      // Update existing preference
      await preference.update({
        enabled: pref.enabled,
        frequency: pref.frequency,
        metadata: pref.metadata || preference.metadata,
      }, { transaction });
    }

    results.push(preference);
  }

  return results;
};

// Instance methods
UserNotificationPreference.prototype.isEnabled = function() {
  return this.enabled && this.frequency !== 'disabled';
};

UserNotificationPreference.prototype.shouldSendImmediate = function() {
  return this.isEnabled() && this.frequency === 'immediate';
};

UserNotificationPreference.prototype.shouldBatch = function() {
  return this.isEnabled() && ['daily', 'weekly'].includes(this.frequency);
};

module.exports = UserNotificationPreference;