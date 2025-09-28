const { sequelize } = require('../config/database');

// Import all models
const Notification = require('./Notification');
const NotificationTemplate = require('./NotificationTemplate');
const NotificationHistory = require('./NotificationHistory');
const UserNotificationPreference = require('./UserNotificationPreference');
const ScheduledNotification = require('./ScheduledNotification');

// Track if associations have been initialized to prevent duplicates
let associationsInitialized = false;

// Define associations
const initializeAssociations = () => {
  if (associationsInitialized) {
    console.log('Database associations already initialized, skipping...');
    return;
  }

  // Notification belongs to NotificationTemplate
  Notification.belongsTo(NotificationTemplate, {
    foreignKey: 'templateId',
    as: 'template',
    onDelete: 'SET NULL',
  });

  // NotificationTemplate has many Notifications
  NotificationTemplate.hasMany(Notification, {
    foreignKey: 'templateId',
    as: 'notifications',
  });

  // Notification has many NotificationHistory records
  Notification.hasMany(NotificationHistory, {
    foreignKey: 'notificationId',
    as: 'history',
    onDelete: 'CASCADE',
  });

  // NotificationHistory belongs to Notification
  NotificationHistory.belongsTo(Notification, {
    foreignKey: 'notificationId',
    as: 'notification',
  });

  // ScheduledNotification belongs to Notification (one-to-one)
  ScheduledNotification.belongsTo(Notification, {
    foreignKey: 'notificationId',
    as: 'notification',
    onDelete: 'CASCADE',
  });

  // Notification has one ScheduledNotification
  Notification.hasOne(ScheduledNotification, {
    foreignKey: 'notificationId',
    as: 'schedule',
  });

  // User-based associations (virtual - no foreign keys to user table)
  // These are helper methods for querying notifications by user

  associationsInitialized = true;
  console.log('Database associations initialized successfully.');
};

// Initialize the database and associations
const initializeDatabase = async(options = {}) => {
  try {
    // Test the connection
    await sequelize.authenticate();
    console.log('Database connection established successfully.');

    // Initialize associations
    initializeAssociations();

    // Sync the database (create tables if they don't exist)
    await sequelize.sync(options);
    console.log('Database synchronized successfully.');

    // Seed default templates if needed
    if (options.seedData !== false) {
      await seedDefaultTemplates();
    }

    return true;
  } catch (error) {
    console.error('Unable to initialize database:', error);
    throw error;
  }
};

// Seed default notification templates
const seedDefaultTemplates = async() => {
  try {
    const templateCount = await NotificationTemplate.count();

    if (templateCount === 0) {
      console.log('Seeding default notification templates...');

      const defaultTemplates = [
        {
          name: 'welcome_email_registration',
          type: 'welcome',
          channel: 'email',
          subject: 'Welcome to Project Zero App, {{userName}}!',
          content: `Dear {{userName}},

Welcome to Project Zero App! We're excited to have you join our community.

To get started, please activate your account by clicking the link below:
{{activationLink}}

If you have any questions, feel free to reach out to our support team.

Best regards,
The Project Zero App Team`,
          variables: {
            userName: { type: 'string', required: true },
            activationLink: { type: 'string', required: true },
          },
          isActive: true,
        },
        {
          name: 'order_email_confirmation',
          type: 'order',
          channel: 'email',
          subject: 'Order Confirmation - {{orderNumber}}',
          content: `Hello {{customerName}},

Thank you for your order! Here are the details:

Order Number: {{orderNumber}}
Order Total: {{orderTotal}}
Estimated Delivery: {{estimatedDelivery}}

Items Ordered:
{{#each orderItems}}
- {{name}}: {{price}}
{{/each}}

We'll send you updates as your order is processed and shipped.

Best regards,
Project Zero Store Team`,
          variables: {
            orderNumber: { type: 'string', required: true },
            customerName: { type: 'string', required: true },
            orderTotal: { type: 'string', required: true },
            estimatedDelivery: { type: 'string', required: true },
            orderItems: { type: 'array', required: true },
          },
          isActive: true,
        },
        {
          name: 'payment_sms_confirmation',
          type: 'payment',
          channel: 'sms',
          subject: null,
          content: 'Payment confirmed: {{amount}} for order {{orderNumber}}. Card ending in {{last4}}. Thank you!',
          variables: {
            amount: { type: 'string', required: true },
            orderNumber: { type: 'string', required: true },
            last4: { type: 'string', required: true },
          },
          isActive: true,
        },
        {
          name: 'system_in_app_maintenance',
          type: 'system',
          channel: 'in_app',
          subject: 'System Maintenance Notice',
          content: 'Scheduled maintenance will occur on {{maintenanceDate}} from {{startTime}} to {{endTime}}. Some features may be temporarily unavailable.',
          variables: {
            maintenanceDate: { type: 'string', required: true },
            startTime: { type: 'string', required: true },
            endTime: { type: 'string', required: true },
          },
          isActive: true,
        },
        {
          name: 'order_sms_shipped',
          type: 'order',
          channel: 'sms',
          subject: null,
          content: 'Good news! Your order {{orderNumber}} has shipped. Track: {{trackingNumber}}',
          variables: {
            orderNumber: { type: 'string', required: true },
            trackingNumber: { type: 'string', required: true },
          },
          isActive: true,
        },
      ];

      await NotificationTemplate.bulkCreate(defaultTemplates);
      console.log(`Seeded ${defaultTemplates.length} default templates.`);
    }
  } catch (error) {
    console.error('Error seeding default templates:', error);
    // Don't throw error here as it's not critical for startup
  }
};

// Close database connections
const closeDatabase = async() => {
  try {
    await sequelize.close();
    console.log('Database connections closed.');
  } catch (error) {
    console.error('Error closing database connections:', error);
  }
};

// Export models and utilities
module.exports = {
  // Database utilities
  sequelize,
  initializeDatabase,
  closeDatabase,
  initializeAssociations,
  seedDefaultTemplates,

  // Models
  Notification,
  NotificationTemplate,
  NotificationHistory,
  UserNotificationPreference,
  ScheduledNotification,

  // Model collections for easy access
  models: {
    Notification,
    NotificationTemplate,
    NotificationHistory,
    UserNotificationPreference,
    ScheduledNotification,
  },
};