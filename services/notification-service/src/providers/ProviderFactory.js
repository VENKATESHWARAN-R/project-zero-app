const MockEmailProvider = require('./MockEmailProvider');
const MockSMSProvider = require('./MockSMSProvider');
const InAppProvider = require('./InAppProvider');

class ProviderFactory {
  constructor() {
    this.providers = new Map();
    this.initializeProviders();
  }

  initializeProviders() {
    // Initialize mock providers
    this.providers.set('email', new MockEmailProvider());
    this.providers.set('sms', new MockSMSProvider());
    this.providers.set('in_app', new InAppProvider());

    console.log('Provider factory initialized with providers:', Array.from(this.providers.keys()));
  }

  getProvider(channel) {
    const provider = this.providers.get(channel);
    if (!provider) {
      throw new Error(`No provider found for channel: ${channel}`);
    }

    if (!provider.isEnabled()) {
      throw new Error(`Provider for channel '${channel}' is disabled`);
    }

    return provider;
  }

  getAllProviders() {
    return Array.from(this.providers.values());
  }

  getEnabledProviders() {
    return Array.from(this.providers.values()).filter(provider => provider.isEnabled());
  }

  getProviderConfig(channel) {
    const provider = this.providers.get(channel);
    if (!provider) {
      throw new Error(`No provider found for channel: ${channel}`);
    }
    return provider.getConfig();
  }

  getAllProviderConfigs() {
    const configs = {};
    for (const [channel, provider] of this.providers.entries()) {
      configs[channel] = provider.getConfig();
    }
    return configs;
  }

  isChannelSupported(channel) {
    return this.providers.has(channel);
  }

  getSupportedChannels() {
    return Array.from(this.providers.keys());
  }

  getEnabledChannels() {
    return Array.from(this.providers.entries())
      .filter(([channel, provider]) => provider.isEnabled())
      .map(([channel]) => channel);
  }

  async testProvider(channel, testData = null) {
    try {
      const provider = this.getProvider(channel);

      const defaultTestData = {
        email: {
          recipient: 'test@example.com',
          subject: 'Test Email',
          content: 'This is a test email from the notification service.',
        },
        sms: {
          recipient: '+1-555-123-4567',
          content: 'Test SMS from notification service.',
        },
        in_app: {
          recipient: 'test-user-123',
          subject: 'Test Notification',
          content: 'This is a test in-app notification.',
        },
      };

      const data = testData || defaultTestData[channel];
      if (!data) {
        throw new Error(`No test data available for channel: ${channel}`);
      }

      const result = await provider.send(data);
      return {
        channel,
        provider: provider.name,
        success: true,
        result,
      };
    } catch (error) {
      return {
        channel,
        provider: this.providers.get(channel)?.name || 'Unknown',
        success: false,
        error: error.message,
      };
    }
  }

  async testAllProviders() {
    const results = {};
    const supportedChannels = this.getSupportedChannels();

    for (const channel of supportedChannels) {
      try {
        results[channel] = await this.testProvider(channel);
      } catch (error) {
        results[channel] = {
          channel,
          provider: 'Unknown',
          success: false,
          error: error.message,
        };
      }
    }

    return results;
  }

  addProvider(channel, provider) {
    if (this.providers.has(channel)) {
      console.warn(`Provider for channel '${channel}' already exists, replacing`);
    }

    this.providers.set(channel, provider);
    console.log(`Added provider for channel: ${channel}`);
  }

  removeProvider(channel) {
    if (this.providers.has(channel)) {
      this.providers.delete(channel);
      console.log(`Removed provider for channel: ${channel}`);
      return true;
    }
    return false;
  }

  getProviderStats() {
    const stats = {
      totalProviders: this.providers.size,
      enabledProviders: 0,
      disabledProviders: 0,
      byChannel: {},
    };

    for (const [channel, provider] of this.providers.entries()) {
      const config = provider.getConfig();
      stats.byChannel[channel] = {
        name: config.name,
        type: config.type,
        enabled: config.enabled,
      };

      if (config.enabled) {
        stats.enabledProviders++;
      } else {
        stats.disabledProviders++;
      }
    }

    return stats;
  }

  validateNotificationData(channel, data) {
    const { recipient, content } = data;

    if (!recipient) {
      return { valid: false, error: 'Recipient is required' };
    }

    if (!content) {
      return { valid: false, error: 'Content is required' };
    }

    // Channel-specific validation
    switch (channel) {
      case 'email':
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(recipient)) {
          return { valid: false, error: 'Invalid email address format' };
        }
        if (!data.subject) {
          return { valid: false, error: 'Subject is required for email notifications' };
        }
        break;

      case 'sms':
        const phoneRegex = /^\+?[1-9]\d{1,14}$/;
        const cleanPhone = recipient.replace(/[\s-()]/g, '');
        if (!phoneRegex.test(cleanPhone)) {
          return { valid: false, error: 'Invalid phone number format' };
        }
        if (content.length > 1600) { // Allow for longer messages that will be segmented
          return { valid: false, error: 'SMS content too long (max 1600 characters)' };
        }
        break;

      case 'in_app':
        if (typeof recipient !== 'string' || recipient.trim() === '') {
          return { valid: false, error: 'Valid user ID required for in-app notifications' };
        }
        break;

      default:
        return { valid: false, error: `Unsupported channel: ${channel}` };
    }

    return { valid: true };
  }
}

module.exports = ProviderFactory;