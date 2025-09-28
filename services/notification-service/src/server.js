const app = require('./app');
const { sequelize, initializeAssociations } = require('./models');
const logger = require('./utils/logger');
const config = require('./config');
const { performFullValidation } = require('./config/validation');

const PORT = config.port || 8011;
const HOST = config.host || '0.0.0.0';

async function startServer() {
  try {
    // Validate environment variables first
    logger.info('Validating environment configuration...');
    const validation = performFullValidation();

    if (!validation.success) {
      logger.error('Environment validation failed:', { errors: validation.errors });
      throw new Error(`Environment validation failed: ${validation.errors.join(', ')}`);
    }

    if (validation.warnings.length > 0) {
      validation.warnings.forEach(warning => {
        logger.warn('Configuration warning:', { warning });
      });
    }

    logger.info('Environment validation successful');
    // Test database connection
    await sequelize.authenticate();
    logger.info('Database connection established successfully');

    // Initialize model associations
    initializeAssociations();
    logger.info('Database associations initialized');

    // Sync database models (create tables if they don't exist)
    if (config.NODE_ENV === 'development') {
      await sequelize.sync({ force: false });
      logger.info('Database models synchronized');
    }

    // Run database migrations
    try {
      const { exec } = require('child_process');
      const { promisify } = require('util');
      const execAsync = promisify(exec);

      // Run migrations if they exist
      const migrationsPath = require('path').join(__dirname, 'migrations');
      const fs = require('fs');

      if (fs.existsSync(migrationsPath)) {
        logger.info('Running database migrations...');
        // Note: In a production environment, you'd use a proper migration tool
        // For now, we'll sync the models which creates tables if they don't exist
        await sequelize.sync({ alter: config.NODE_ENV === 'development' });
        logger.info('Database migrations completed');
      }
    } catch (migrationError) {
      logger.logError(migrationError, null, { component: 'database-migrations' });
      // Don't fail startup if migrations fail, but log the error
    }

    // Seed default templates if in development mode
    if (config.NODE_ENV === 'development') {
      try {
        await seedDefaultTemplates();
        logger.info('Default templates seeded');
      } catch (seedError) {
        logger.logError(seedError, null, { component: 'template-seeding' });
      }
    }

    // Start the server
    const server = app.listen(PORT, HOST, () => {
      logger.info(`Notification service started`, {
        port: PORT,
        host: HOST,
        environment: config.NODE_ENV,
        docs: `http://${HOST}:${PORT}/docs`,
        health: `http://${HOST}:${PORT}/health`
      });
    });

    // Graceful shutdown
    const gracefulShutdown = async () => {
      logger.info('Shutting down server gracefully...');

      server.close(async () => {
        logger.info('HTTP server closed');

        try {
          await sequelize.close();
          logger.info('Database connection closed');
        } catch (error) {
          logger.logError(error, null, { component: 'database-shutdown' });
        }

        process.exit(0);
      });

      // Force shutdown after 10 seconds
      setTimeout(() => {
        logger.error('Could not close connections in time, forcefully shutting down');
        process.exit(1);
      }, 10000);
    };

    process.on('SIGTERM', gracefulShutdown);
    process.on('SIGINT', gracefulShutdown);

  } catch (error) {
    logger.logError(error, null, { component: 'server-startup' });
    process.exit(1);
  }
}

async function seedDefaultTemplates() {
  const { NotificationTemplate } = require('./models');

  const defaultTemplates = [
    {
      name: 'welcome_email_registration',
      type: 'welcome',
      channel: 'email',
      subject: 'Welcome to Project Zero App, {{userName}}!',
      content: `Hello {{userName}},

Welcome to Project Zero App! We're excited to have you join our community.

To get started, please click the link below to activate your account:
{{activationLink}}

If you have any questions, please don't hesitate to contact our support team.

Best regards,
The Project Zero App Team`,
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
      content: `Hello {{customerName}},

Thank you for your order! Here are the details:

Order Number: {{orderNumber}}
Total Amount: {{orderTotal}}

Items:
{{#each orderItems}}
- {{name}}: {{price}}
{{/each}}

Estimated Delivery: {{estimatedDelivery}}

You can track your order status in your account dashboard.

Thank you for shopping with Project Zero App!`,
      variables: {
        customerName: { type: 'string', required: true },
        orderNumber: { type: 'string', required: true },
        orderTotal: { type: 'string', required: true },
        orderItems: { type: 'array', required: true },
        estimatedDelivery: { type: 'string', required: true }
      },
      isActive: true
    },
    {
      name: 'payment_sms_confirmation',
      type: 'payment',
      channel: 'sms',
      content: 'Payment confirmed! Amount: {{amount}} for order {{orderNumber}}. Card ending in {{last4}}. Thank you!',
      variables: {
        amount: { type: 'string', required: true },
        orderNumber: { type: 'string', required: true },
        last4: { type: 'string', required: true }
      },
      isActive: true
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
        endTime: { type: 'string', required: true }
      },
      isActive: true
    }
  ];

  for (const templateData of defaultTemplates) {
    try {
      const [template, created] = await NotificationTemplate.findOrCreate({
        where: { name: templateData.name },
        defaults: templateData
      });

      if (created) {
        logger.info(`Created default template: ${templateData.name}`);
      }
    } catch (error) {
      logger.logError(error, null, {
        component: 'template-seeding',
        templateName: templateData.name
      });
    }
  }
}

// Start the server
if (require.main === module) {
  startServer();
}

module.exports = { startServer };