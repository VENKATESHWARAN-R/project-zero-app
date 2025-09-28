const { DataTypes } = require('sequelize');

module.exports = {
  up: async(queryInterface, Sequelize) => {
    // Create notification_templates table first (referenced by notifications)
    await queryInterface.createTable('notification_templates', {
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
      },
      name: {
        type: DataTypes.STRING(255),
        allowNull: false,
        unique: true,
      },
      type: {
        type: DataTypes.ENUM('welcome', 'order', 'payment', 'system', 'promotional'),
        allowNull: false,
      },
      channel: {
        type: DataTypes.ENUM('email', 'sms', 'in_app'),
        allowNull: false,
      },
      subject: {
        type: DataTypes.STRING(500),
        allowNull: true,
      },
      content: {
        type: DataTypes.TEXT,
        allowNull: false,
      },
      variables: {
        type: DataTypes.JSON,
        allowNull: true,
      },
      isActive: {
        type: DataTypes.BOOLEAN,
        allowNull: false,
        defaultValue: true,
      },
      createdAt: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP'),
      },
      updatedAt: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP'),
      },
    });

    // Create notifications table
    await queryInterface.createTable('notifications', {
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
      },
      userId: {
        type: DataTypes.STRING(255),
        allowNull: false,
      },
      templateId: {
        type: DataTypes.UUID,
        allowNull: true,
        references: {
          model: 'notification_templates',
          key: 'id',
        },
        onUpdate: 'CASCADE',
        onDelete: 'SET NULL',
      },
      channel: {
        type: DataTypes.ENUM('email', 'sms', 'in_app'),
        allowNull: false,
      },
      recipient: {
        type: DataTypes.STRING(255),
        allowNull: false,
      },
      subject: {
        type: DataTypes.STRING(500),
        allowNull: true,
      },
      content: {
        type: DataTypes.TEXT,
        allowNull: false,
      },
      metadata: {
        type: DataTypes.JSON,
        allowNull: true,
      },
      status: {
        type: DataTypes.ENUM('pending', 'sent', 'delivered', 'failed'),
        allowNull: false,
        defaultValue: 'pending',
      },
      scheduledAt: {
        type: DataTypes.DATE,
        allowNull: true,
      },
      sentAt: {
        type: DataTypes.DATE,
        allowNull: true,
      },
      deliveredAt: {
        type: DataTypes.DATE,
        allowNull: true,
      },
      failureReason: {
        type: DataTypes.TEXT,
        allowNull: true,
      },
      priority: {
        type: DataTypes.ENUM('low', 'normal', 'high'),
        allowNull: false,
        defaultValue: 'normal',
      },
      createdAt: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP'),
      },
      updatedAt: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP'),
      },
    });

    // Create notification_history table
    await queryInterface.createTable('notification_history', {
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
      },
      notificationId: {
        type: DataTypes.UUID,
        allowNull: false,
        references: {
          model: 'notifications',
          key: 'id',
        },
        onUpdate: 'CASCADE',
        onDelete: 'CASCADE',
      },
      userId: {
        type: DataTypes.STRING(255),
        allowNull: false,
      },
      event: {
        type: DataTypes.ENUM('created', 'sent', 'delivered', 'failed', 'retried'),
        allowNull: false,
      },
      previousStatus: {
        type: DataTypes.ENUM('pending', 'sent', 'delivered', 'failed'),
        allowNull: true,
      },
      newStatus: {
        type: DataTypes.ENUM('pending', 'sent', 'delivered', 'failed'),
        allowNull: true,
      },
      details: {
        type: DataTypes.JSON,
        allowNull: true,
      },
      providerId: {
        type: DataTypes.STRING(255),
        allowNull: true,
      },
      errorCode: {
        type: DataTypes.STRING(100),
        allowNull: true,
      },
      errorMessage: {
        type: DataTypes.TEXT,
        allowNull: true,
      },
      timestamp: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP'),
      },
    });

    // Create user_notification_preferences table
    await queryInterface.createTable('user_notification_preferences', {
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
      },
      userId: {
        type: DataTypes.STRING(255),
        allowNull: false,
      },
      type: {
        type: DataTypes.ENUM('welcome', 'order', 'payment', 'system', 'promotional'),
        allowNull: false,
      },
      channel: {
        type: DataTypes.ENUM('email', 'sms', 'in_app'),
        allowNull: false,
      },
      enabled: {
        type: DataTypes.BOOLEAN,
        allowNull: false,
        defaultValue: true,
      },
      frequency: {
        type: DataTypes.ENUM('immediate', 'daily', 'weekly', 'disabled'),
        allowNull: false,
        defaultValue: 'immediate',
      },
      metadata: {
        type: DataTypes.JSON,
        allowNull: true,
      },
      createdAt: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP'),
      },
      updatedAt: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP'),
      },
    });

    // Create scheduled_notifications table
    await queryInterface.createTable('scheduled_notifications', {
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
      },
      notificationId: {
        type: DataTypes.UUID,
        allowNull: false,
        unique: true,
        references: {
          model: 'notifications',
          key: 'id',
        },
        onUpdate: 'CASCADE',
        onDelete: 'CASCADE',
      },
      scheduledAt: {
        type: DataTypes.DATE,
        allowNull: false,
      },
      attempts: {
        type: DataTypes.INTEGER,
        allowNull: false,
        defaultValue: 0,
      },
      maxAttempts: {
        type: DataTypes.INTEGER,
        allowNull: false,
        defaultValue: 3,
      },
      retryInterval: {
        type: DataTypes.INTEGER,
        allowNull: false,
        defaultValue: 300,
      },
      status: {
        type: DataTypes.ENUM('scheduled', 'processing', 'sent', 'failed'),
        allowNull: false,
        defaultValue: 'scheduled',
      },
      lastAttemptAt: {
        type: DataTypes.DATE,
        allowNull: true,
      },
      nextAttemptAt: {
        type: DataTypes.DATE,
        allowNull: true,
      },
      errorDetails: {
        type: DataTypes.JSON,
        allowNull: true,
      },
      createdAt: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP'),
      },
      updatedAt: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP'),
      },
    });

    // Create indexes for notification_templates
    await queryInterface.addIndex('notification_templates', ['name'], {
      unique: true,
      name: 'idx_notification_templates_name',
    });
    await queryInterface.addIndex('notification_templates', ['type', 'channel'], {
      name: 'idx_notification_templates_type_channel',
    });
    await queryInterface.addIndex('notification_templates', ['isActive'], {
      name: 'idx_notification_templates_active',
    });

    // Create indexes for notifications
    await queryInterface.addIndex('notifications', ['userId'], {
      name: 'idx_notifications_user_id',
    });
    await queryInterface.addIndex('notifications', ['status'], {
      name: 'idx_notifications_status',
    });
    await queryInterface.addIndex('notifications', ['scheduledAt'], {
      name: 'idx_notifications_scheduled_at',
    });
    await queryInterface.addIndex('notifications', ['createdAt'], {
      name: 'idx_notifications_created_at',
    });
    await queryInterface.addIndex('notifications', ['channel'], {
      name: 'idx_notifications_channel',
    });

    // Create indexes for notification_history
    await queryInterface.addIndex('notification_history', ['notificationId'], {
      name: 'idx_notification_history_notification_id',
    });
    await queryInterface.addIndex('notification_history', ['userId'], {
      name: 'idx_notification_history_user_id',
    });
    await queryInterface.addIndex('notification_history', ['event'], {
      name: 'idx_notification_history_event',
    });
    await queryInterface.addIndex('notification_history', ['timestamp'], {
      name: 'idx_notification_history_timestamp',
    });

    // Create indexes for user_notification_preferences
    await queryInterface.addIndex('user_notification_preferences', ['userId'], {
      name: 'idx_user_notification_preferences_user_id',
    });
    await queryInterface.addIndex('user_notification_preferences', ['type', 'channel'], {
      name: 'idx_user_notification_preferences_type_channel',
    });
    await queryInterface.addIndex('user_notification_preferences', ['userId', 'type', 'channel'], {
      unique: true,
      name: 'unique_user_type_channel',
    });

    // Create indexes for scheduled_notifications
    await queryInterface.addIndex('scheduled_notifications', ['scheduledAt'], {
      name: 'idx_scheduled_notifications_scheduled_at',
    });
    await queryInterface.addIndex('scheduled_notifications', ['status'], {
      name: 'idx_scheduled_notifications_status',
    });
    await queryInterface.addIndex('scheduled_notifications', ['nextAttemptAt'], {
      name: 'idx_scheduled_notifications_next_attempt',
    });

    console.log('All notification service tables and indexes created successfully.');
  },

  down: async(queryInterface, Sequelize) => {
    // Drop tables in reverse order to handle foreign key constraints
    await queryInterface.dropTable('scheduled_notifications');
    await queryInterface.dropTable('user_notification_preferences');
    await queryInterface.dropTable('notification_history');
    await queryInterface.dropTable('notifications');
    await queryInterface.dropTable('notification_templates');

    console.log('All notification service tables dropped successfully.');
  },
};