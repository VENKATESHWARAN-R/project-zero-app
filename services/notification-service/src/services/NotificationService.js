const { Notification, NotificationHistory, UserNotificationPreference } = require('../models');
const ProviderFactory = require('../providers/ProviderFactory');

class NotificationService {
  constructor() {
    this.providerFactory = new ProviderFactory();
  }

  /**
   * Create and send a new notification
   */
  async createNotification(notificationData) {
    try {
      // Validate user preferences before creating notification
      const isAllowed = await UserNotificationPreference.isAllowed(
        notificationData.userId,
        notificationData.metadata?.type || 'system',
        notificationData.channel
      );

      if (!isAllowed) {
        throw new Error(`Notifications of type '${notificationData.metadata?.type}' via '${notificationData.channel}' are disabled for this user`);
      }

      // Create the notification record
      const notification = await Notification.create({
        userId: notificationData.userId,
        templateId: notificationData.templateId,
        channel: notificationData.channel,
        recipient: notificationData.recipient,
        subject: notificationData.subject,
        content: notificationData.content,
        metadata: notificationData.metadata || {},
        status: 'pending',
        scheduledAt: notificationData.scheduledAt,
        priority: notificationData.priority || 'normal',
      });

      // Log creation in history
      await NotificationHistory.logCreated(notification.id, notification.userId, {
        channel: notification.channel,
        recipient: notification.recipient,
        templateId: notification.templateId,
      });

      // Send immediately if not scheduled
      if (!notification.scheduledAt || new Date(notification.scheduledAt) <= new Date()) {
        await this.sendNotification(notification.id);
      }

      return await this.getNotificationById(notification.id);
    } catch (error) {
      console.error('Error creating notification:', error);
      throw error;
    }
  }

  /**
   * Send a notification using the appropriate provider
   */
  async sendNotification(notificationId) {
    try {
      const notification = await Notification.findByPk(notificationId);
      if (!notification) {
        throw new Error('Notification not found');
      }

      if (notification.status !== 'pending') {
        throw new Error(`Cannot send notification with status: ${notification.status}`);
      }

      // Get the appropriate provider
      const provider = this.providerFactory.getProvider(notification.channel);

      // Update status to indicate sending is in progress
      await notification.update({ status: 'pending' });

      try {
        // Send the notification
        const result = await provider.send({
          recipient: notification.recipient,
          subject: notification.subject,
          content: notification.content,
          metadata: notification.metadata,
        });

        // Mark as sent
        await notification.markAsSent();

        // Log sent event
        await NotificationHistory.logSent(
          notification.id,
          notification.userId,
          result.providerId,
          {
            providerResponse: result,
            sentAt: new Date(),
          }
        );

        // Simulate delivery confirmation for mock providers
        if (result.delivered) {
          await notification.markAsDelivered();
          await NotificationHistory.logDelivered(
            notification.id,
            notification.userId,
            result.providerId,
            {
              deliveredAt: new Date(),
            }
          );
        }

        return await this.getNotificationById(notification.id);
      } catch (sendError) {
        // Mark as failed
        await notification.markAsFailed(sendError.message);

        // Log failure
        await NotificationHistory.logFailed(
          notification.id,
          notification.userId,
          sendError.code || 'SEND_ERROR',
          sendError.message,
          {
            error: sendError.message,
            failedAt: new Date(),
          }
        );

        throw sendError;
      }
    } catch (error) {
      console.error('Error sending notification:', error);
      throw error;
    }
  }

  /**
   * Get notification by ID
   */
  async getNotificationById(notificationId, userId = null) {
    try {
      const whereClause = { id: notificationId };
      if (userId) {
        whereClause.userId = userId;
      }

      const notification = await Notification.findOne({
        where: whereClause,
        include: [
          {
            association: 'template',
            attributes: ['id', 'name', 'type', 'channel'],
          },
          {
            association: 'schedule',
            attributes: ['id', 'scheduledAt', 'attempts', 'maxAttempts', 'status', 'nextAttemptAt'],
          },
        ],
      });

      if (!notification) {
        throw new Error('Notification not found');
      }

      return notification;
    } catch (error) {
      console.error('Error getting notification:', error);
      throw error;
    }
  }

  /**
   * Get notifications for a user with pagination and filtering
   */
  async getUserNotifications(userId, options = {}) {
    try {
      const {
        page = 1,
        limit = 20,
        channel,
        status,
        startDate,
        endDate,
      } = options;

      const offset = (page - 1) * limit;
      const whereClause = { userId };

      // Add filters
      if (channel) {
        whereClause.channel = channel;
      }
      if (status) {
        whereClause.status = status;
      }
      if (startDate || endDate) {
        whereClause.createdAt = {};
        if (startDate) {
          whereClause.createdAt[Notification.sequelize.Op.gte] = new Date(startDate);
        }
        if (endDate) {
          whereClause.createdAt[Notification.sequelize.Op.lte] = new Date(endDate);
        }
      }

      const { count, rows: notifications } = await Notification.findAndCountAll({
        where: whereClause,
        limit: parseInt(limit),
        offset: parseInt(offset),
        order: [['createdAt', 'DESC']],
        include: [
          {
            association: 'template',
            attributes: ['id', 'name', 'type'],
          },
        ],
      });

      const totalPages = Math.ceil(count / limit);

      return {
        notifications,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          totalPages,
          totalCount: count,
          hasNext: page < totalPages,
          hasPrevious: page > 1,
        },
      };
    } catch (error) {
      console.error('Error getting user notifications:', error);
      throw error;
    }
  }

  /**
   * Get notification history
   */
  async getNotificationHistory(notificationId) {
    try {
      const history = await NotificationHistory.findByNotification(notificationId);
      return history;
    } catch (error) {
      console.error('Error getting notification history:', error);
      throw error;
    }
  }

  /**
   * Retry a failed notification
   */
  async retryNotification(notificationId) {
    try {
      const notification = await Notification.findByPk(notificationId);
      if (!notification) {
        throw new Error('Notification not found');
      }

      if (!notification.canRetry()) {
        throw new Error('Notification cannot be retried');
      }

      // Reset status to pending
      await notification.update({
        status: 'pending',
        failureReason: null,
      });

      // Log retry event
      await NotificationHistory.logRetried(notification.id, notification.userId, {
        retriedAt: new Date(),
        previousFailureReason: notification.failureReason,
      });

      // Send the notification
      return await this.sendNotification(notification.id);
    } catch (error) {
      console.error('Error retrying notification:', error);
      throw error;
    }
  }

  /**
   * Get pending notifications that need to be sent
   */
  async getPendingNotifications(limit = 100) {
    try {
      return await Notification.findPending({ limit });
    } catch (error) {
      console.error('Error getting pending notifications:', error);
      throw error;
    }
  }

  /**
   * Get scheduled notifications ready for delivery
   */
  async getScheduledNotifications(beforeDate = new Date(), limit = 100) {
    try {
      return await Notification.findScheduled(beforeDate, { limit });
    } catch (error) {
      console.error('Error getting scheduled notifications:', error);
      throw error;
    }
  }

  /**
   * Process a batch of notifications
   */
  async processBatch(notificationIds) {
    const results = [];

    for (const notificationId of notificationIds) {
      try {
        const result = await this.sendNotification(notificationId);
        results.push({ notificationId, success: true, result });
      } catch (error) {
        results.push({
          notificationId,
          success: false,
          error: error.message,
        });
      }
    }

    return results;
  }

  /**
   * Cancel a scheduled notification
   */
  async cancelNotification(notificationId, userId = null) {
    try {
      const whereClause = { id: notificationId };
      if (userId) {
        whereClause.userId = userId;
      }

      const notification = await Notification.findOne({ where: whereClause });
      if (!notification) {
        throw new Error('Notification not found');
      }

      if (notification.status !== 'pending') {
        throw new Error('Only pending notifications can be cancelled');
      }

      await notification.update({ status: 'failed', failureReason: 'Cancelled by user' });

      return notification;
    } catch (error) {
      console.error('Error cancelling notification:', error);
      throw error;
    }
  }

  /**
   * Get notification statistics
   */
  async getStats(userId = null, timeRange = '24h') {
    try {
      const whereClause = {};
      if (userId) {
        whereClause.userId = userId;
      }

      // Calculate time range
      const now = new Date();
      let startDate;
      switch (timeRange) {
        case '1h':
          startDate = new Date(now.getTime() - 60 * 60 * 1000);
          break;
        case '24h':
          startDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
          break;
        case '7d':
          startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          break;
        case '30d':
          startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          break;
        default:
          startDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      }

      whereClause.createdAt = {
        [Notification.sequelize.Op.gte]: startDate,
      };

      const stats = await Notification.findAll({
        where: whereClause,
        attributes: [
          'status',
          'channel',
          [Notification.sequelize.fn('COUNT', '*'), 'count'],
        ],
        group: ['status', 'channel'],
        raw: true,
      });

      // Format the stats
      const result = {
        timeRange,
        startDate,
        endDate: now,
        total: 0,
        byStatus: {},
        byChannel: {},
      };

      stats.forEach(stat => {
        const count = parseInt(stat.count);
        result.total += count;

        if (!result.byStatus[stat.status]) {
          result.byStatus[stat.status] = 0;
        }
        result.byStatus[stat.status] += count;

        if (!result.byChannel[stat.channel]) {
          result.byChannel[stat.channel] = 0;
        }
        result.byChannel[stat.channel] += count;
      });

      return result;
    } catch (error) {
      console.error('Error getting notification stats:', error);
      throw error;
    }
  }
}

module.exports = NotificationService;