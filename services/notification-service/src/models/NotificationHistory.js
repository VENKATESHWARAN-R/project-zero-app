const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const NotificationHistory = sequelize.define('NotificationHistory', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  notificationId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'notifications',
      key: 'id',
    },
  },
  userId: {
    type: DataTypes.STRING(255),
    allowNull: false,
    validate: {
      notEmpty: true,
    },
  },
  event: {
    type: DataTypes.ENUM('created', 'sent', 'delivered', 'failed', 'retried'),
    allowNull: false,
    validate: {
      isIn: [['created', 'sent', 'delivered', 'failed', 'retried']],
    },
  },
  previousStatus: {
    type: DataTypes.ENUM('pending', 'sent', 'delivered', 'failed'),
    allowNull: true,
  },
  newStatus: {
    type: DataTypes.ENUM('pending', 'sent', 'delivered', 'failed'),
    allowNull: true,
  },
  details: {
    type: DataTypes.JSON,
    allowNull: true,
    defaultValue: {},
  },
  providerId: {
    type: DataTypes.STRING(255),
    allowNull: true,
  },
  errorCode: {
    type: DataTypes.STRING(100),
    allowNull: true,
  },
  errorMessage: {
    type: DataTypes.TEXT,
    allowNull: true,
  },
  timestamp: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
    validate: {
      isDate: true,
      notInFuture(value) {
        if (new Date(value) > new Date()) {
          throw new Error('History timestamp cannot be in the future');
        }
      },
    },
  },
}, {
  tableName: 'notification_history',
  timestamps: false, // We use our own timestamp field
  indexes: [
    {
      fields: ['notificationId'],
      name: 'idx_notification_history_notification_id',
    },
    {
      fields: ['userId'],
      name: 'idx_notification_history_user_id',
    },
    {
      fields: ['event'],
      name: 'idx_notification_history_event',
    },
    {
      fields: ['timestamp'],
      name: 'idx_notification_history_timestamp',
    },
    {
      fields: ['notificationId', 'timestamp'],
      name: 'idx_notification_history_notification_timestamp',
    },
  ],
  validate: {
    statusTransitionValid() {
      if (this.previousStatus && this.newStatus) {
        const validTransitions = {
          pending: ['sent', 'failed'],
          sent: ['delivered', 'failed'],
          delivered: [], // Terminal state
          failed: ['pending'], // Can retry
        };

        const allowedNextStates = validTransitions[this.previousStatus] || [];
        if (!allowedNextStates.includes(this.newStatus)) {
          throw new Error(`Invalid status transition from ${this.previousStatus} to ${this.newStatus}`);
        }
      }
    },
  },
});

// Class methods for creating history entries
NotificationHistory.logCreated = function(notificationId, userId, details = {}) {
  return this.create({
    notificationId,
    userId,
    event: 'created',
    newStatus: 'pending',
    details,
  });
};

NotificationHistory.logSent = function(notificationId, userId, providerId = null, details = {}) {
  return this.create({
    notificationId,
    userId,
    event: 'sent',
    previousStatus: 'pending',
    newStatus: 'sent',
    providerId,
    details,
  });
};

NotificationHistory.logDelivered = function(notificationId, userId, providerId = null, details = {}) {
  return this.create({
    notificationId,
    userId,
    event: 'delivered',
    previousStatus: 'sent',
    newStatus: 'delivered',
    providerId,
    details,
  });
};

NotificationHistory.logFailed = function(notificationId, userId, errorCode = null, errorMessage = null, details = {}) {
  return this.create({
    notificationId,
    userId,
    event: 'failed',
    previousStatus: 'pending',
    newStatus: 'failed',
    errorCode,
    errorMessage,
    details,
  });
};

NotificationHistory.logRetried = function(notificationId, userId, details = {}) {
  return this.create({
    notificationId,
    userId,
    event: 'retried',
    previousStatus: 'failed',
    newStatus: 'pending',
    details,
  });
};

NotificationHistory.findByNotification = function(notificationId, options = {}) {
  return this.findAll({
    where: { notificationId },
    order: [['timestamp', 'ASC']],
    ...options,
  });
};

NotificationHistory.findByUser = function(userId, options = {}) {
  return this.findAll({
    where: { userId },
    order: [['timestamp', 'DESC']],
    ...options,
  });
};

NotificationHistory.findByDateRange = function(startDate, endDate, options = {}) {
  return this.findAll({
    where: {
      timestamp: {
        [sequelize.Sequelize.Op.between]: [startDate, endDate],
      },
    },
    order: [['timestamp', 'DESC']],
    ...options,
  });
};

// Instance methods
NotificationHistory.prototype.isError = function() {
  return this.event === 'failed' && (this.errorCode || this.errorMessage);
};

NotificationHistory.prototype.isSuccess = function() {
  return ['sent', 'delivered'].includes(this.event);
};

module.exports = NotificationHistory;