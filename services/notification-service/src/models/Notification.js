const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Notification = sequelize.define('Notification', {
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
  templateId: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'notification_templates',
      key: 'id',
    },
  },
  channel: {
    type: DataTypes.ENUM('email', 'sms', 'in_app'),
    allowNull: false,
    validate: {
      isIn: [['email', 'sms', 'in_app']],
    },
  },
  recipient: {
    type: DataTypes.STRING(255),
    allowNull: false,
    validate: {
      notEmpty: true,
      isValidRecipient(value) {
        if (this.channel === 'email') {
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(value)) {
            throw new Error('Invalid email format');
          }
        } else if (this.channel === 'sms') {
          const phoneRegex = /^\+?[1-9]\d{1,14}$/;
          if (!phoneRegex.test(value.replace(/[\s-()]/g, ''))) {
            throw new Error('Invalid phone number format');
          }
        }
      },
    },
  },
  subject: {
    type: DataTypes.STRING(500),
    allowNull: true,
  },
  content: {
    type: DataTypes.TEXT,
    allowNull: false,
    validate: {
      notEmpty: true,
    },
  },
  metadata: {
    type: DataTypes.JSON,
    allowNull: true,
    defaultValue: {},
  },
  status: {
    type: DataTypes.ENUM('pending', 'sent', 'delivered', 'failed'),
    allowNull: false,
    defaultValue: 'pending',
    validate: {
      isIn: [['pending', 'sent', 'delivered', 'failed']],
    },
  },
  scheduledAt: {
    type: DataTypes.DATE,
    allowNull: true,
    validate: {
      isDate: true,
      isFuture(value) {
        if (value && new Date(value) <= new Date()) {
          throw new Error('Scheduled time must be in the future');
        }
      },
    },
  },
  sentAt: {
    type: DataTypes.DATE,
    allowNull: true,
    validate: {
      isDate: true,
    },
  },
  deliveredAt: {
    type: DataTypes.DATE,
    allowNull: true,
    validate: {
      isDate: true,
      isAfterSent(value) {
        if (value && this.sentAt && new Date(value) < new Date(this.sentAt)) {
          throw new Error('Delivery time must be after sent time');
        }
      },
    },
  },
  failureReason: {
    type: DataTypes.TEXT,
    allowNull: true,
  },
  priority: {
    type: DataTypes.ENUM('low', 'normal', 'high'),
    allowNull: false,
    defaultValue: 'normal',
  },
}, {
  tableName: 'notifications',
  indexes: [
    {
      fields: ['userId'],
      name: 'idx_notifications_user_id',
    },
    {
      fields: ['status'],
      name: 'idx_notifications_status',
    },
    {
      fields: ['scheduledAt'],
      name: 'idx_notifications_scheduled_at',
    },
    {
      fields: ['createdAt'],
      name: 'idx_notifications_created_at',
    },
    {
      fields: ['channel'],
      name: 'idx_notifications_channel',
    },
  ],
  hooks: {
    beforeUpdate: async(notification, options) => {
      // Update sentAt when status changes to sent
      if (notification.status === 'sent' && !notification.sentAt) {
        notification.sentAt = new Date();
      }
      // Update deliveredAt when status changes to delivered
      if (notification.status === 'delivered' && !notification.deliveredAt) {
        notification.deliveredAt = new Date();
      }
    },
  },
});

// Instance methods
Notification.prototype.markAsSent = function() {
  this.status = 'sent';
  this.sentAt = new Date();
  return this.save();
};

Notification.prototype.markAsDelivered = function() {
  this.status = 'delivered';
  this.deliveredAt = new Date();
  return this.save();
};

Notification.prototype.markAsFailed = function(reason) {
  this.status = 'failed';
  this.failureReason = reason;
  return this.save();
};

Notification.prototype.canRetry = function() {
  return this.status === 'failed' || this.status === 'pending';
};

// Class methods
Notification.findByUser = function(userId, options = {}) {
  return this.findAll({
    where: { userId },
    order: [['createdAt', 'DESC']],
    ...options,
  });
};

Notification.findPending = function(options = {}) {
  return this.findAll({
    where: { status: 'pending' },
    order: [['createdAt', 'ASC']],
    ...options,
  });
};

Notification.findScheduled = function(beforeDate = new Date(), options = {}) {
  return this.findAll({
    where: {
      status: 'pending',
      scheduledAt: {
        [sequelize.Sequelize.Op.lte]: beforeDate,
      },
    },
    order: [['scheduledAt', 'ASC']],
    ...options,
  });
};

module.exports = Notification;