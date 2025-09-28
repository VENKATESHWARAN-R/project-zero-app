const { ScheduledNotification, Notification } = require('../models');
const NotificationService = require('./NotificationService');

class SchedulerService {
  constructor() {
    this.notificationService = new NotificationService();
    this.isRunning = false;
    this.intervalId = null;
  }

  /**
   * Start the scheduler
   */
  start(intervalSeconds = 60) {
    if (this.isRunning) {
      console.log('Scheduler is already running');
      return;
    }

    this.isRunning = true;
    console.log(`Starting notification scheduler with ${intervalSeconds}s interval`);

    this.intervalId = setInterval(async() => {
      try {
        await this.processScheduledNotifications();
      } catch (error) {
        console.error('Error in scheduler processing:', error);
      }
    }, intervalSeconds * 1000);
  }

  /**
   * Stop the scheduler
   */
  stop() {
    if (!this.isRunning) {
      console.log('Scheduler is not running');
      return;
    }

    this.isRunning = false;
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    console.log('Notification scheduler stopped');
  }

  /**
   * Schedule a notification for future delivery
   */
  async scheduleNotification(notificationData) {
    try {
      const { scheduledAt, maxAttempts = 3, retryInterval = 300, ...notificationFields } = notificationData;

      if (!scheduledAt) {
        throw new Error('scheduledAt is required for scheduled notifications');
      }

      const scheduledDate = new Date(scheduledAt);
      if (scheduledDate <= new Date()) {
        throw new Error('Scheduled time must be in the future');
      }

      // Create the notification first
      const notification = await Notification.create({
        ...notificationFields,
        status: 'pending',
        scheduledAt: scheduledDate,
      });

      // Create the scheduled notification entry
      const scheduledNotification = await ScheduledNotification.create({
        notificationId: notification.id,
        scheduledAt: scheduledDate,
        maxAttempts,
        retryInterval,
        status: 'scheduled',
        nextAttemptAt: scheduledDate,
      });

      return {
        notification,
        schedule: scheduledNotification,
      };
    } catch (error) {
      console.error('Error scheduling notification:', error);
      throw error;
    }
  }

  /**
   * Process all scheduled notifications that are ready for delivery
   */
  async processScheduledNotifications() {
    try {
      const currentTime = new Date();
      const readyNotifications = await ScheduledNotification.findReadyForDelivery(currentTime, {
        limit: 100, // Process in batches
        include: [
          {
            association: 'notification',
            required: true,
          },
        ],
      });

      if (readyNotifications.length === 0) {
        return { processed: 0, successful: 0, failed: 0 };
      }

      console.log(`Processing ${readyNotifications.length} scheduled notifications`);

      const results = {
        processed: readyNotifications.length,
        successful: 0,
        failed: 0,
        details: [],
      };

      for (const scheduledNotification of readyNotifications) {
        try {
          await this.processSingleScheduledNotification(scheduledNotification);
          results.successful++;
          results.details.push({
            id: scheduledNotification.id,
            notificationId: scheduledNotification.notificationId,
            success: true,
          });
        } catch (error) {
          results.failed++;
          results.details.push({
            id: scheduledNotification.id,
            notificationId: scheduledNotification.notificationId,
            success: false,
            error: error.message,
          });
          console.error(`Error processing scheduled notification ${scheduledNotification.id}:`, error);
        }
      }

      console.log(`Scheduler processed: ${results.successful} successful, ${results.failed} failed`);
      return results;
    } catch (error) {
      console.error('Error in processScheduledNotifications:', error);
      throw error;
    }
  }

  /**
   * Process a single scheduled notification
   */
  async processSingleScheduledNotification(scheduledNotification) {
    try {
      // Mark as processing
      await scheduledNotification.markAsProcessing();

      // Send the notification
      await this.notificationService.sendNotification(scheduledNotification.notificationId);

      // Mark as sent
      await scheduledNotification.markAsSent();

      console.log(`Successfully sent scheduled notification ${scheduledNotification.id}`);
    } catch (error) {
      // Mark as failed and handle retry logic
      await scheduledNotification.markAsFailed({
        error: error.message,
        timestamp: new Date(),
      });

      throw error;
    }
  }

  /**
   * Reschedule a failed notification
   */
  async rescheduleNotification(scheduledNotificationId, newScheduledAt) {
    try {
      const scheduledNotification = await ScheduledNotification.findByPk(scheduledNotificationId);
      if (!scheduledNotification) {
        throw new Error('Scheduled notification not found');
      }

      await scheduledNotification.reschedule(newScheduledAt);
      return scheduledNotification;
    } catch (error) {
      console.error('Error rescheduling notification:', error);
      throw error;
    }
  }

  /**
   * Cancel a scheduled notification
   */
  async cancelScheduledNotification(scheduledNotificationId) {
    try {
      const scheduledNotification = await ScheduledNotification.findByPk(scheduledNotificationId, {
        include: [{ association: 'notification' }],
      });

      if (!scheduledNotification) {
        throw new Error('Scheduled notification not found');
      }

      if (scheduledNotification.status !== 'scheduled') {
        throw new Error('Only scheduled notifications can be cancelled');
      }

      // Update the scheduled notification
      await scheduledNotification.update({
        status: 'failed',
        errorDetails: {
          cancelled: true,
          cancelledAt: new Date(),
        },
      });

      // Update the associated notification
      await scheduledNotification.notification.update({
        status: 'failed',
        failureReason: 'Cancelled',
      });

      return scheduledNotification;
    } catch (error) {
      console.error('Error cancelling scheduled notification:', error);
      throw error;
    }
  }

  /**
   * Get scheduled notifications by status
   */
  async getScheduledNotificationsByStatus(status, options = {}) {
    try {
      return await ScheduledNotification.findByStatus(status, {
        include: [
          {
            association: 'notification',
            attributes: ['id', 'userId', 'channel', 'recipient', 'subject', 'content'],
          },
        ],
        ...options,
      });
    } catch (error) {
      console.error('Error getting scheduled notifications by status:', error);
      throw error;
    }
  }

  /**
   * Get pending retries
   */
  async getPendingRetries(options = {}) {
    try {
      return await ScheduledNotification.findPendingRetries({
        include: [
          {
            association: 'notification',
            attributes: ['id', 'userId', 'channel', 'recipient', 'failureReason'],
          },
        ],
        ...options,
      });
    } catch (error) {
      console.error('Error getting pending retries:', error);
      throw error;
    }
  }

  /**
   * Clean up old completed/failed scheduled notifications
   */
  async cleanup(olderThanDays = 7) {
    try {
      const olderThan = new Date(Date.now() - olderThanDays * 24 * 60 * 60 * 1000);
      return await ScheduledNotification.cleanupExpired(olderThan);
    } catch (error) {
      console.error('Error cleaning up scheduled notifications:', error);
      throw error;
    }
  }

  /**
   * Get scheduler statistics
   */
  async getStats() {
    try {
      const scheduledStats = await ScheduledNotification.getStats();

      // Get additional timing information
      const now = new Date();
      const upcomingCount = await ScheduledNotification.count({
        where: {
          status: 'scheduled',
          nextAttemptAt: {
            [ScheduledNotification.sequelize.Op.between]: [
              now,
              new Date(now.getTime() + 60 * 60 * 1000), // Next hour
            ],
          },
        },
      });

      const overdueCount = await ScheduledNotification.count({
        where: {
          status: 'scheduled',
          nextAttemptAt: {
            [ScheduledNotification.sequelize.Op.lt]: now,
          },
        },
      });

      return {
        ...scheduledStats,
        upcoming: upcomingCount,
        overdue: overdueCount,
        isRunning: this.isRunning,
        lastProcessed: this.lastProcessed || null,
      };
    } catch (error) {
      console.error('Error getting scheduler stats:', error);
      throw error;
    }
  }

  /**
   * Force process a specific scheduled notification
   */
  async forceProcessNotification(scheduledNotificationId) {
    try {
      const scheduledNotification = await ScheduledNotification.findByPk(scheduledNotificationId, {
        include: [{ association: 'notification' }],
      });

      if (!scheduledNotification) {
        throw new Error('Scheduled notification not found');
      }

      if (scheduledNotification.status !== 'scheduled') {
        throw new Error('Only scheduled notifications can be force processed');
      }

      await this.processSingleScheduledNotification(scheduledNotification);
      return scheduledNotification;
    } catch (error) {
      console.error('Error force processing notification:', error);
      throw error;
    }
  }

  /**
   * Get scheduler status
   */
  getStatus() {
    return {
      isRunning: this.isRunning,
      intervalId: this.intervalId !== null,
      lastProcessed: this.lastProcessed || null,
    };
  }

  /**
   * Bulk reschedule notifications
   */
  async bulkReschedule(scheduledNotificationIds, newScheduledAt) {
    try {
      const results = [];

      for (const id of scheduledNotificationIds) {
        try {
          const rescheduled = await this.rescheduleNotification(id, newScheduledAt);
          results.push({ id, success: true, notification: rescheduled });
        } catch (error) {
          results.push({ id, success: false, error: error.message });
        }
      }

      return results;
    } catch (error) {
      console.error('Error bulk rescheduling notifications:', error);
      throw error;
    }
  }
}

module.exports = SchedulerService;