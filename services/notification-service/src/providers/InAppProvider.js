const config = require('../config');

class InAppProvider {
  constructor() {
    this.name = 'InAppProvider';
    this.type = 'in_app';
    this.config = config.providers.inApp;
  }

  async send(notificationData) {
    try {
      const { recipient, subject, content, metadata } = notificationData;

      // For in-app notifications, recipient is typically a user ID
      if (!recipient) {
        throw new Error('Recipient user ID is required for in-app notifications');
      }

      // Simulate processing delay (minimal for in-app)
      if (this.config.mockDelay > 0) {
        await new Promise(resolve => setTimeout(resolve, this.config.mockDelay));
      }

      // In-app notifications rarely fail in mock scenarios
      const providerId = `inapp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const deliveryTime = new Date();

      console.log(`[MOCK IN-APP] Sent to user: ${recipient}`);
      console.log(`[MOCK IN-APP] Subject: ${subject || 'No subject'}`);
      console.log(`[MOCK IN-APP] Content: ${content}`);

      // Simulate storing in user's notification inbox
      const notificationPayload = {
        id: providerId,
        userId: recipient,
        subject: subject || 'Notification',
        content,
        metadata: {
          provider: this.name,
          ...metadata,
        },
        createdAt: deliveryTime,
        readAt: null,
        isRead: false,
      };

      // In real implementation, this would be stored in a user notifications table
      // or sent via WebSocket/SSE to connected clients
      console.log(`[MOCK IN-APP] Stored notification:`, notificationPayload);

      return {
        success: true,
        providerId,
        recipient,
        channel: 'in_app',
        sentAt: deliveryTime,
        delivered: true, // In-app notifications are immediately "delivered"
        deliveredAt: deliveryTime,
        metadata: {
          provider: this.name,
          notificationId: providerId,
          stored: true,
          ...metadata,
        },
      };
    } catch (error) {
      console.error(`[MOCK IN-APP] Failed to send to ${notificationData.recipient}:`, error.message);
      throw error;
    }
  }

  async getDeliveryStatus(providerId) {
    // Mock delivery status check
    return {
      providerId,
      status: 'delivered',
      deliveredAt: new Date(),
      readAt: null,
      isRead: false,
      events: [
        { event: 'sent', timestamp: new Date(Date.now() - 100) },
        { event: 'delivered', timestamp: new Date() },
      ],
    };
  }

  async markAsRead(providerId, userId) {
    // Mock marking notification as read
    console.log(`[MOCK IN-APP] Marking notification ${providerId} as read for user ${userId}`);
    return {
      providerId,
      userId,
      readAt: new Date(),
      isRead: true,
    };
  }

  async getUserNotifications(userId, options = {}) {
    // Mock getting user's in-app notifications
    const { limit = 20, includeRead = true } = options;

    console.log(`[MOCK IN-APP] Getting notifications for user ${userId} (limit: ${limit})`);

    // In real implementation, this would query a database
    return {
      userId,
      notifications: [],
      unreadCount: 0,
      totalCount: 0,
    };
  }

  isEnabled() {
    return this.config.enabled;
  }

  getConfig() {
    return {
      name: this.name,
      type: this.type,
      enabled: this.config.enabled,
      mockDelay: this.config.mockDelay,
    };
  }
}

module.exports = InAppProvider;