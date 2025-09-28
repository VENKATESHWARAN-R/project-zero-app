const config = require('../config');

class MockEmailProvider {
  constructor() {
    this.name = 'MockEmailProvider';
    this.type = 'email';
    this.config = config.providers.email;
  }

  async send(notificationData) {
    try {
      const { recipient, subject, content, metadata } = notificationData;

      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(recipient)) {
        throw new Error('Invalid email address format');
      }

      // Simulate processing delay
      if (this.config.mockDelay > 0) {
        await new Promise(resolve => setTimeout(resolve, this.config.mockDelay));
      }

      // Simulate random failures
      if (Math.random() < this.config.failureRate) {
        throw new Error('Simulated email delivery failure');
      }

      // Mock successful delivery
      const providerId = `email_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const deliveryTime = new Date();

      console.log(`[MOCK EMAIL] Sent to: ${recipient}`);
      console.log(`[MOCK EMAIL] Subject: ${subject}`);
      console.log(`[MOCK EMAIL] Content length: ${content.length} chars`);

      return {
        success: true,
        providerId,
        recipient,
        channel: 'email',
        sentAt: deliveryTime,
        delivered: true,
        deliveredAt: deliveryTime,
        metadata: {
          provider: this.name,
          messageId: providerId,
          ...metadata,
        },
      };
    } catch (error) {
      console.error(`[MOCK EMAIL] Failed to send to ${notificationData.recipient}:`, error.message);
      throw error;
    }
  }

  async getDeliveryStatus(providerId) {
    // Mock delivery status check
    return {
      providerId,
      status: 'delivered',
      deliveredAt: new Date(),
      events: [
        { event: 'sent', timestamp: new Date(Date.now() - 1000) },
        { event: 'delivered', timestamp: new Date() },
      ],
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
      failureRate: this.config.failureRate,
    };
  }
}

module.exports = MockEmailProvider;