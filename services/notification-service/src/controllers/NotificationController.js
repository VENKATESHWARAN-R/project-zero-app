const NotificationService = require('../services/NotificationService');
const TemplateService = require('../services/TemplateService');
const SchedulerService = require('../services/SchedulerService');

// Create service instances
const notificationService = new NotificationService();
const templateService = new TemplateService();
const schedulerService = new SchedulerService();

class NotificationController {
  static async sendNotification(req, res) {
    try {
      const { userId, channel, recipient, subject, content, metadata, priority = 'normal' } = req.body;

      if (!userId || !channel || !recipient || !content) {
        return res.status(400).json({
          error: 'validation_error',
          message: 'Missing required fields: userId, channel, recipient, content',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      const notification = await notificationService.createNotification({
        userId,
        channel,
        recipient,
        subject,
        content,
        metadata,
        priority
      });

      res.status(201).json(notification);
    } catch (error) {
      console.error('Error sending notification:', error);
      res.status(500).json({
        error: 'internal_error',
        message: 'Failed to send notification',
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }
  }

  static async getNotifications(req, res) {
    try {
      const userId = req.user.userId;
      const { page = 1, limit = 20, channel, status, startDate, endDate } = req.query;

      const options = {
        page: parseInt(page),
        limit: parseInt(limit),
        channel,
        status,
        startDate,
        endDate
      };

      const result = await notificationService.getUserNotifications(userId, options);
      res.status(200).json(result);
    } catch (error) {
      console.error('Error getting notifications:', error);
      res.status(500).json({
        error: 'internal_error',
        message: 'Failed to retrieve notifications',
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }
  }

  static async getNotificationById(req, res) {
    try {
      const { id } = req.params;
      const userId = req.user.userId;

      const notification = await notificationService.getNotificationById(id, userId);

      if (!notification) {
        return res.status(404).json({
          error: 'not_found',
          message: 'Notification not found',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      res.status(200).json(notification);
    } catch (error) {
      console.error('Error getting notification:', error);
      res.status(500).json({
        error: 'internal_error',
        message: 'Failed to retrieve notification',
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }
  }

  static async scheduleNotification(req, res) {
    try {
      const { userId, channel, recipient, subject, content, metadata, scheduledAt, maxAttempts = 3, retryInterval = 300 } = req.body;

      if (!userId || !channel || !recipient || !content || !scheduledAt) {
        return res.status(400).json({
          error: 'validation_error',
          message: 'Missing required fields: userId, channel, recipient, content, scheduledAt',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      const scheduledDate = new Date(scheduledAt);
      if (scheduledDate <= new Date()) {
        return res.status(400).json({
          error: 'validation_error',
          message: 'Scheduled time must be in the future',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      const result = await schedulerService.scheduleNotification({
        userId,
        channel,
        recipient,
        subject,
        content,
        metadata,
        scheduledAt: scheduledDate,
        maxAttempts,
        retryInterval
      });

      res.status(201).json(result);
    } catch (error) {
      console.error('Error scheduling notification:', error);
      res.status(500).json({
        error: 'internal_error',
        message: 'Failed to schedule notification',
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }
  }

  static async sendTemplateNotification(req, res) {
    try {
      const { userId, templateName, variables, recipient, scheduledAt } = req.body;

      if (!userId || !templateName || !variables) {
        return res.status(400).json({
          error: 'validation_error',
          message: 'Missing required fields: userId, templateName, variables',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      const template = await templateService.getTemplateByName(templateName);
      if (!template) {
        return res.status(404).json({
          error: 'not_found',
          message: 'Template not found',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      if (!template.isActive) {
        return res.status(400).json({
          error: 'validation_error',
          message: 'Template is not active',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      const renderedNotification = template.render(variables);

      // Generate recipient if not provided
      let finalRecipient = recipient;
      if (!finalRecipient) {
        if (template.channel === 'email') {
          finalRecipient = `${userId}@example.com`; // Placeholder for development
        } else if (template.channel === 'sms') {
          finalRecipient = `+1-555-${userId.slice(-7)}`; // Placeholder for development
        } else {
          finalRecipient = userId; // For in-app notifications
        }
      }

      const notificationData = {
        userId,
        templateId: template.id,
        channel: template.channel,
        recipient: finalRecipient,
        subject: renderedNotification.subject,
        content: renderedNotification.content,
        metadata: { templateName, variables }
      };

      let result;
      if (scheduledAt) {
        const scheduledDate = new Date(scheduledAt);
        if (scheduledDate <= new Date()) {
          return res.status(400).json({
            error: 'validation_error',
            message: 'Scheduled time must be in the future',
            timestamp: new Date().toISOString(),
            path: req.path
          });
        }
        result = await schedulerService.scheduleNotification({
          ...notificationData,
          scheduledAt: scheduledDate
        });
      } else {
        result = await notificationService.createNotification(notificationData);
      }

      res.status(201).json(result);
    } catch (error) {
      console.error('Error sending template notification:', error);
      res.status(500).json({
        error: 'internal_error',
        message: 'Failed to send template notification',
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }
  }
}

module.exports = NotificationController;