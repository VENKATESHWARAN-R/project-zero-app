const { testConnection, closeConnection } = require('../src/config/database');
const { initializeAssociations, sequelize, NotificationTemplate } = require('../src/models');

// Global test setup
beforeAll(async() => {
  // Set test environment
  process.env.NODE_ENV = 'test';
  process.env.DATABASE_URL = 'sqlite::memory:';
  process.env.JWT_SECRET_KEY = 'test-secret-key';
  process.env.LOG_LEVEL = 'error';

  // Test database connection
  const connected = await testConnection();
  if (!connected) {
    throw new Error('Failed to connect to test database');
  }

  // Initialize associations
  initializeAssociations();

  // Sync models for tests
  await sequelize.sync({ force: true });

  // Seed test templates
  await seedTestTemplates();
});

// Global test cleanup
afterAll(async() => {
  await closeConnection();
});

// Add custom matchers if needed
expect.extend({
  toBeValidUUID(received) {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    const pass = uuidRegex.test(received);
    if (pass) {
      return {
        message: () => `expected ${received} not to be a valid UUID`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${received} to be a valid UUID`,
        pass: false,
      };
    }
  },
});

// Seed test templates
async function seedTestTemplates() {
  const testTemplates = [
    {
      name: 'welcome_email_registration',
      type: 'welcome',
      channel: 'email',
      subject: 'Welcome to Project Zero App, {{userName}}!',
      content: 'Hello {{userName}}, welcome to our platform! {{activationLink}}',
      variables: {
        userName: { type: 'string', required: true },
        activationLink: { type: 'string', required: true }
      },
      isActive: true
    },
    {
      name: 'order_email_confirmation',
      type: 'order',
      channel: 'email',
      subject: 'Order Confirmation - {{orderNumber}}',
      content: 'Hello {{customerName}}, your order {{orderNumber}} for {{orderTotal}} has been confirmed.',
      variables: {
        customerName: { type: 'string', required: true },
        orderNumber: { type: 'string', required: true },
        orderTotal: { type: 'string', required: true }
      },
      isActive: true
    },
    {
      name: 'payment_sms_confirmation',
      type: 'payment',
      channel: 'sms',
      content: 'Payment confirmed: {{amount}} for order {{orderNumber}}.',
      variables: {
        amount: { type: 'string', required: true },
        orderNumber: { type: 'string', required: true }
      },
      isActive: true
    }
  ];

  await NotificationTemplate.bulkCreate(testTemplates);
}