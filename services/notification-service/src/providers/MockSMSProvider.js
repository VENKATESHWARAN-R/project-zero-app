const config = require('../config');

class MockSMSProvider {
  constructor() {
    this.name = 'MockSMSProvider';
    this.type = 'sms';
    this.config = config.providers.sms;
  }

  async send(notificationData) {
    try {
      const { recipient, content, metadata } = notificationData;

      // Validate phone number format
      const phoneRegex = /^\+?[1-9]\d{1,14}$/;
      const cleanPhone = recipient.replace(/[\s-()]/g, '');
      if (!phoneRegex.test(cleanPhone)) {
        throw new Error('Invalid phone number format');
      }

      // Validate SMS length
      if (content.length > 160) {
        console.warn(`[MOCK SMS] Message length (${content.length}) exceeds 160 characters, may be split`);
      }

      // Simulate processing delay
      if (this.config.mockDelay > 0) {
        await new Promise(resolve => setTimeout(resolve, this.config.mockDelay));
      }

      // Simulate random failures
      if (Math.random() < this.config.failureRate) {
        throw new Error('Simulated SMS delivery failure');
      }

      // Mock successful delivery
      const providerId = `sms_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const deliveryTime = new Date();

      console.log(`[MOCK SMS] Sent to: ${recipient}`);
      console.log(`[MOCK SMS] Content: ${content}`);
      console.log(`[MOCK SMS] Length: ${content.length} chars`);

      return {
        success: true,
        providerId,
        recipient,
        channel: 'sms',
        sentAt: deliveryTime,
        delivered: true,
        deliveredAt: deliveryTime,
        metadata: {
          provider: this.name,
          messageId: providerId,
          messageLength: content.length,
          segmentCount: Math.ceil(content.length / 160),
          ...metadata,
        },
      };
    } catch (error) {
      console.error(`[MOCK SMS] Failed to send to ${notificationData.recipient}:`, error.message);
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
        { event: 'sent', timestamp: new Date(Date.now() - 500) },
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

module.exports = MockSMSProvider;