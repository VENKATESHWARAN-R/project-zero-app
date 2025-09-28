const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const ScheduledNotification = sequelize.define('ScheduledNotification', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  notificationId: {
    type: DataTypes.UUID,
    allowNull: false,
    unique: true,
    references: {
      model: 'notifications',
      key: 'id',
    },
  },
  scheduledAt: {
    type: DataTypes.DATE,
    allowNull: false,
    validate: {
      isDate: true,
      isFutureWhenCreated(value) {
        if (this.isNewRecord && new Date(value) <= new Date()) {
          throw new Error('Scheduled time must be in the future');
        }
      },
    },
  },
  attempts: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 0,
    validate: {
      min: 0,
    },
  },
  maxAttempts: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 3,
    validate: {
      min: 1,
      max: 10,
    },
  },
  retryInterval: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 300, // 5 minutes in seconds
    validate: {
      min: 60, // Minimum 1 minute
    },
  },
  status: {
    type: DataTypes.ENUM('scheduled', 'processing', 'sent', 'failed'),
    allowNull: false,
    defaultValue: 'scheduled',
    validate: {
      isIn: [['scheduled', 'processing', 'sent', 'failed']],
    },
  },
  lastAttemptAt: {
    type: DataTypes.DATE,
    allowNull: true,
    validate: {
      isDate: true,
    },
  },
  nextAttemptAt: {
    type: DataTypes.DATE,
    allowNull: true,
    validate: {
      isDate: true,
      isAfterLastAttempt(value) {
        if (value && this.lastAttemptAt && new Date(value) <= new Date(this.lastAttemptAt)) {
          throw new Error('Next attempt must be after last attempt');
        }
      },
    },
  },
  errorDetails: {
    type: DataTypes.JSON,
    allowNull: true,
    defaultValue: {},
  },
}, {
  tableName: 'scheduled_notifications',
  indexes: [
    {
      fields: ['scheduledAt'],
      name: 'idx_scheduled_notifications_scheduled_at',
    },
    {
      fields: ['status'],
      name: 'idx_scheduled_notifications_status',
    },
    {
      fields: ['nextAttemptAt'],
      name: 'idx_scheduled_notifications_next_attempt',
    },
    {
      fields: ['status', 'scheduledAt'],
      name: 'idx_scheduled_notifications_status_scheduled',
    },
    {
      fields: ['status', 'nextAttemptAt'],
      name: 'idx_scheduled_notifications_status_next_attempt',
    },
  ],
  hooks: {
    beforeCreate: async(scheduledNotification, options) => {
      // Set initial nextAttemptAt to scheduledAt
      if (!scheduledNotification.nextAttemptAt) {
        scheduledNotification.nextAttemptAt = scheduledNotification.scheduledAt;
      }
    },
  },
});

// Instance methods
ScheduledNotification.prototype.canRetry = function() {
  return this.attempts < this.maxAttempts && this.status !== 'sent';
};

ScheduledNotification.prototype.markAsProcessing = function() {
  this.status = 'processing';
  this.lastAttemptAt = new Date();
  this.attempts += 1;
  return this.save();
};

ScheduledNotification.prototype.markAsSent = function() {
  this.status = 'sent';
  this.nextAttemptAt = null;
  return this.save();
};

ScheduledNotification.prototype.markAsFailed = function(errorDetails = {}) {
  if (this.canRetry()) {
    // Schedule next retry
    const nextAttempt = new Date(Date.now() + (this.retryInterval * 1000));
    this.nextAttemptAt = nextAttempt;
    this.status = 'scheduled';
  } else {
    // Max attempts reached
    this.status = 'failed';
    this.nextAttemptAt = null;
  }

  this.errorDetails = {
    ...this.errorDetails,
    lastError: errorDetails,
    failedAt: new Date(),
  };

  return this.save();
};

ScheduledNotification.prototype.reschedule = function(newScheduledAt) {
  if (new Date(newScheduledAt) <= new Date()) {
    throw new Error('New scheduled time must be in the future');
  }

  this.scheduledAt = newScheduledAt;
  this.nextAttemptAt = newScheduledAt;
  this.status = 'scheduled';
  this.attempts = 0;
  this.lastAttemptAt = null;
  this.errorDetails = {};

  return this.save();
};

ScheduledNotification.prototype.getRemainingAttempts = function() {
  return Math.max(0, this.maxAttempts - this.attempts);
};

ScheduledNotification.prototype.getTimeToNextAttempt = function() {
  if (!this.nextAttemptAt) return null;
  return Math.max(0, new Date(this.nextAttemptAt).getTime() - Date.now());
};

// Class methods
ScheduledNotification.findReadyForDelivery = function(currentTime = new Date(), options = {}) {
  return this.findAll({
    where: {
      status: 'scheduled',
      nextAttemptAt: {
        [sequelize.Sequelize.Op.lte]: currentTime,
      },
    },
    order: [['nextAttemptAt', 'ASC']],
    ...options,
  });
};

ScheduledNotification.findByStatus = function(status, options = {}) {
  return this.findAll({
    where: { status },
    order: [['scheduledAt', 'ASC']],
    ...options,
  });
};

ScheduledNotification.findPendingRetries = function(options = {}) {
  return this.findAll({
    where: {
      status: 'scheduled',
      attempts: {
        [sequelize.Sequelize.Op.gt]: 0,
      },
    },
    order: [['nextAttemptAt', 'ASC']],
    ...options,
  });
};

ScheduledNotification.findExpired = function(olderThan = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), options = {}) {
  return this.findAll({
    where: {
      status: 'failed',
      updatedAt: {
        [sequelize.Sequelize.Op.lt]: olderThan,
      },
    },
    order: [['updatedAt', 'ASC']],
    ...options,
  });
};

ScheduledNotification.cleanupExpired = async function(olderThan = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)) {
  const expiredNotifications = await this.findExpired(olderThan);
  const deletedCount = await this.destroy({
    where: {
      id: {
        [sequelize.Sequelize.Op.in]: expiredNotifications.map(n => n.id),
      },
    },
  });

  return {
    found: expiredNotifications.length,
    deleted: deletedCount,
  };
};

ScheduledNotification.getStats = async function() {
  const stats = await this.findAll({
    attributes: [
      'status',
      [sequelize.fn('COUNT', '*'), 'count'],
    ],
    group: ['status'],
    raw: true,
  });

  const result = {
    total: 0,
    scheduled: 0,
    processing: 0,
    sent: 0,
    failed: 0,
  };

  stats.forEach(stat => {
    result[stat.status] = parseInt(stat.count);
    result.total += parseInt(stat.count);
  });

  return result;
};

module.exports = ScheduledNotification;