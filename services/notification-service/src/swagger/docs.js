/**
 * Comprehensive Swagger documentation for the Notification Service API
 * This file contains complete OpenAPI 3.0 specifications for all endpoints
 * based on the contracts/notification-api.yaml specification
 */

const swaggerJSDocs = {
  openapi: '3.0.3',
  info: {
    title: 'Notification Service API',
    description: 'Project Zero App notification service for handling all user communications',
    version: '1.0.0',
    contact: {
      name: 'Project Zero App Team',
      url: 'https://github.com/project-zero-app'
    }
  },
  servers: [
    {
      url: 'http://localhost:8011',
      description: 'Local development server'
    },
    {
      url: 'http://notification-service:8011',
      description: 'Docker container'
    }
  ],
  paths: {
    '/health': {
      get: {
        summary: 'Health check endpoint',
        description: 'Basic health check for service availability',
        tags: ['Health'],
        responses: {
          '200': {
            description: 'Service is healthy',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/HealthResponse' }
              }
            }
          }
        }
      }
    },
    '/health/ready': {
      get: {
        summary: 'Readiness check endpoint',
        description: 'Readiness check including database connectivity',
        tags: ['Health'],
        responses: {
          '200': {
            description: 'Service is ready',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ReadinessResponse' }
              }
            }
          },
          '503': {
            description: 'Service is not ready',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          }
        }
      }
    },
    '/notifications': {
      post: {
        summary: 'Send immediate notification',
        description: 'Send a notification immediately to a user',
        tags: ['Notifications'],
        security: [{ bearerAuth: [] }],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/SendNotificationRequest' }
            }
          }
        },
        responses: {
          '201': {
            description: 'Notification created and sent',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/NotificationResponse' }
              }
            }
          },
          '400': {
            description: 'Invalid request data',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          },
          '422': {
            description: 'Validation error',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ValidationErrorResponse' }
              }
            }
          }
        }
      },
      get: {
        summary: 'Get notification history',
        description: 'Retrieve notification history for the authenticated user',
        tags: ['Notifications'],
        security: [{ bearerAuth: [] }],
        parameters: [
          {
            name: 'page',
            in: 'query',
            description: 'Page number for pagination',
            required: false,
            schema: { type: 'integer', minimum: 1, default: 1 }
          },
          {
            name: 'limit',
            in: 'query',
            description: 'Number of notifications per page',
            required: false,
            schema: { type: 'integer', minimum: 1, maximum: 100, default: 20 }
          },
          {
            name: 'channel',
            in: 'query',
            description: 'Filter by notification channel',
            required: false,
            schema: { type: 'string', enum: ['email', 'sms', 'in_app'] }
          },
          {
            name: 'status',
            in: 'query',
            description: 'Filter by notification status',
            required: false,
            schema: { type: 'string', enum: ['pending', 'sent', 'delivered', 'failed'] }
          },
          {
            name: 'startDate',
            in: 'query',
            description: 'Filter notifications from this date (ISO 8601)',
            required: false,
            schema: { type: 'string', format: 'date-time' }
          },
          {
            name: 'endDate',
            in: 'query',
            description: 'Filter notifications until this date (ISO 8601)',
            required: false,
            schema: { type: 'string', format: 'date-time' }
          }
        ],
        responses: {
          '200': {
            description: 'Notification history retrieved',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/NotificationHistoryResponse' }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          }
        }
      }
    },
    '/notifications/{id}': {
      get: {
        summary: 'Get notification details',
        description: 'Retrieve details of a specific notification',
        tags: ['Notifications'],
        security: [{ bearerAuth: [] }],
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            description: 'Notification ID',
            schema: { type: 'string', format: 'uuid' }
          }
        ],
        responses: {
          '200': {
            description: 'Notification details',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/NotificationResponse' }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          },
          '404': {
            description: 'Notification not found',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          }
        }
      }
    },
    '/notifications/schedule': {
      post: {
        summary: 'Schedule notification',
        description: 'Schedule a notification for future delivery',
        tags: ['Notifications'],
        security: [{ bearerAuth: [] }],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/ScheduleNotificationRequest' }
            }
          }
        },
        responses: {
          '201': {
            description: 'Notification scheduled',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ScheduledNotificationResponse' }
              }
            }
          },
          '400': {
            description: 'Invalid request data',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          }
        }
      }
    },
    '/notifications/template': {
      post: {
        summary: 'Send notification using template',
        description: 'Send a notification using a predefined template',
        tags: ['Notifications'],
        security: [{ bearerAuth: [] }],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/TemplateNotificationRequest' }
            }
          }
        },
        responses: {
          '201': {
            description: 'Template notification sent',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/NotificationResponse' }
              }
            }
          },
          '400': {
            description: 'Invalid request data',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          }
        }
      }
    },
    '/templates': {
      get: {
        summary: 'List notification templates',
        description: 'Get all available notification templates',
        tags: ['Templates'],
        security: [{ bearerAuth: [] }],
        parameters: [
          {
            name: 'type',
            in: 'query',
            description: 'Filter by template type',
            required: false,
            schema: { type: 'string', enum: ['welcome', 'order', 'payment', 'system', 'promotional'] }
          },
          {
            name: 'channel',
            in: 'query',
            description: 'Filter by channel',
            required: false,
            schema: { type: 'string', enum: ['email', 'sms', 'in_app'] }
          },
          {
            name: 'active',
            in: 'query',
            description: 'Filter by active status',
            required: false,
            schema: { type: 'boolean' }
          }
        ],
        responses: {
          '200': {
            description: 'Templates retrieved',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/TemplateListResponse' }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          }
        }
      },
      post: {
        summary: 'Create notification template',
        description: 'Create a new notification template (admin only)',
        tags: ['Templates'],
        security: [{ bearerAuth: [] }],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/CreateTemplateRequest' }
            }
          }
        },
        responses: {
          '201': {
            description: 'Template created',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/TemplateResponse' }
              }
            }
          },
          '400': {
            description: 'Invalid request data',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          },
          '403': {
            description: 'Forbidden - admin access required',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          }
        }
      }
    },
    '/templates/{id}': {
      get: {
        summary: 'Get template details',
        description: 'Retrieve details of a specific template',
        tags: ['Templates'],
        security: [{ bearerAuth: [] }],
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            description: 'Template ID',
            schema: { type: 'string', format: 'uuid' }
          }
        ],
        responses: {
          '200': {
            description: 'Template details',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/TemplateResponse' }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          },
          '404': {
            description: 'Template not found',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          }
        }
      },
      put: {
        summary: 'Update notification template',
        description: 'Update an existing notification template (admin only)',
        tags: ['Templates'],
        security: [{ bearerAuth: [] }],
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            description: 'Template ID',
            schema: { type: 'string', format: 'uuid' }
          }
        ],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/UpdateTemplateRequest' }
            }
          }
        },
        responses: {
          '200': {
            description: 'Template updated',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/TemplateResponse' }
              }
            }
          },
          '400': {
            description: 'Invalid request data',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          },
          '403': {
            description: 'Forbidden - admin access required',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          },
          '404': {
            description: 'Template not found',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          }
        }
      }
    },
    '/preferences': {
      get: {
        summary: 'Get user notification preferences',
        description: 'Retrieve notification preferences for the authenticated user',
        tags: ['Preferences'],
        security: [{ bearerAuth: [] }],
        responses: {
          '200': {
            description: 'User preferences retrieved',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/PreferencesResponse' }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          }
        }
      },
      put: {
        summary: 'Update user notification preferences',
        description: 'Update notification preferences for the authenticated user',
        tags: ['Preferences'],
        security: [{ bearerAuth: [] }],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/UpdatePreferencesRequest' }
            }
          }
        },
        responses: {
          '200': {
            description: 'Preferences updated',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/PreferencesResponse' }
              }
            }
          },
          '400': {
            description: 'Invalid request data',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          }
        }
      }
    }
  },
  components: {
    securitySchemes: {
      bearerAuth: {
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT'
      }
    },
    schemas: {
      HealthResponse: {
        type: 'object',
        properties: {
          status: { type: 'string', enum: ['healthy'] },
          service: { type: 'string', example: 'notification-service' },
          version: { type: 'string', example: '1.0.0' },
          timestamp: { type: 'string', format: 'date-time' }
        }
      },
      ReadinessResponse: {
        type: 'object',
        properties: {
          status: { type: 'string', enum: ['ready'] },
          checks: {
            type: 'object',
            properties: {
              database: { type: 'string', enum: ['ok', 'error'] },
              auth_service: { type: 'string', enum: ['ok', 'error'] }
            }
          },
          timestamp: { type: 'string', format: 'date-time' }
        }
      },
      SendNotificationRequest: {
        type: 'object',
        required: ['userId', 'channel', 'recipient', 'content'],
        properties: {
          userId: { type: 'string', description: 'Target user ID' },
          channel: { type: 'string', enum: ['email', 'sms', 'in_app'], description: 'Notification delivery channel' },
          recipient: { type: 'string', description: 'Email address or phone number' },
          subject: { type: 'string', description: 'Email subject or SMS preview', maxLength: 500 },
          content: { type: 'string', description: 'Notification body content' },
          metadata: { type: 'object', description: 'Additional context data' },
          priority: { type: 'string', enum: ['low', 'normal', 'high'], default: 'normal' }
        }
      },
      ScheduleNotificationRequest: {
        type: 'object',
        required: ['userId', 'channel', 'recipient', 'content', 'scheduledAt'],
        allOf: [
          { $ref: '#/components/schemas/SendNotificationRequest' },
          {
            type: 'object',
            properties: {
              scheduledAt: { type: 'string', format: 'date-time', description: 'When to send the notification' },
              maxAttempts: { type: 'integer', minimum: 1, maximum: 10, default: 3, description: 'Maximum retry attempts' },
              retryInterval: { type: 'integer', minimum: 60, default: 300, description: 'Seconds between retries' }
            }
          }
        ]
      },
      TemplateNotificationRequest: {
        type: 'object',
        required: ['userId', 'templateName', 'variables'],
        properties: {
          userId: { type: 'string', description: 'Target user ID' },
          templateName: { type: 'string', description: 'Name of the template to use' },
          variables: { type: 'object', description: 'Template variable values' },
          recipient: { type: 'string', description: 'Override recipient (optional)' },
          scheduledAt: { type: 'string', format: 'date-time', description: 'Schedule for future delivery (optional)' }
        }
      },
      NotificationResponse: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' },
          userId: { type: 'string' },
          templateId: { type: 'string', format: 'uuid' },
          channel: { type: 'string', enum: ['email', 'sms', 'in_app'] },
          recipient: { type: 'string' },
          subject: { type: 'string' },
          content: { type: 'string' },
          metadata: { type: 'object' },
          status: { type: 'string', enum: ['pending', 'sent', 'delivered', 'failed'] },
          scheduledAt: { type: 'string', format: 'date-time' },
          sentAt: { type: 'string', format: 'date-time' },
          deliveredAt: { type: 'string', format: 'date-time' },
          failureReason: { type: 'string' },
          createdAt: { type: 'string', format: 'date-time' },
          updatedAt: { type: 'string', format: 'date-time' }
        }
      },
      ScheduledNotificationResponse: {
        type: 'object',
        allOf: [
          { $ref: '#/components/schemas/NotificationResponse' },
          {
            type: 'object',
            properties: {
              scheduleId: { type: 'string', format: 'uuid' },
              attempts: { type: 'integer' },
              maxAttempts: { type: 'integer' },
              nextAttemptAt: { type: 'string', format: 'date-time' }
            }
          }
        ]
      },
      NotificationHistoryResponse: {
        type: 'object',
        properties: {
          notifications: {
            type: 'array',
            items: { $ref: '#/components/schemas/NotificationResponse' }
          },
          pagination: {
            type: 'object',
            properties: {
              page: { type: 'integer' },
              limit: { type: 'integer' },
              totalPages: { type: 'integer' },
              totalCount: { type: 'integer' },
              hasNext: { type: 'boolean' },
              hasPrevious: { type: 'boolean' }
            }
          }
        }
      },
      CreateTemplateRequest: {
        type: 'object',
        required: ['name', 'type', 'channel', 'content'],
        properties: {
          name: { type: 'string', description: 'Unique template name', pattern: '^[a-z]+_[a-z]+_[a-z_]+$' },
          type: { type: 'string', enum: ['welcome', 'order', 'payment', 'system', 'promotional'] },
          channel: { type: 'string', enum: ['email', 'sms', 'in_app'] },
          subject: { type: 'string', maxLength: 500, description: 'Template subject (for email)' },
          content: { type: 'string', description: 'Template content with variables' },
          variables: { type: 'object', description: 'Available template variables schema' },
          isActive: { type: 'boolean', default: true }
        }
      },
      UpdateTemplateRequest: {
        type: 'object',
        properties: {
          subject: { type: 'string', maxLength: 500 },
          content: { type: 'string' },
          variables: { type: 'object' },
          isActive: { type: 'boolean' }
        }
      },
      TemplateResponse: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' },
          name: { type: 'string' },
          type: { type: 'string', enum: ['welcome', 'order', 'payment', 'system', 'promotional'] },
          channel: { type: 'string', enum: ['email', 'sms', 'in_app'] },
          subject: { type: 'string' },
          content: { type: 'string' },
          variables: { type: 'object' },
          isActive: { type: 'boolean' },
          createdAt: { type: 'string', format: 'date-time' },
          updatedAt: { type: 'string', format: 'date-time' }
        }
      },
      TemplateListResponse: {
        type: 'object',
        properties: {
          templates: {
            type: 'array',
            items: { $ref: '#/components/schemas/TemplateResponse' }
          }
        }
      },
      UpdatePreferencesRequest: {
        type: 'object',
        properties: {
          preferences: {
            type: 'array',
            items: {
              type: 'object',
              required: ['type', 'channel', 'enabled'],
              properties: {
                type: { type: 'string', enum: ['welcome', 'order', 'payment', 'system', 'promotional'] },
                channel: { type: 'string', enum: ['email', 'sms', 'in_app'] },
                enabled: { type: 'boolean' },
                frequency: { type: 'string', enum: ['immediate', 'daily', 'weekly', 'disabled'] }
              }
            }
          }
        }
      },
      PreferencesResponse: {
        type: 'object',
        properties: {
          userId: { type: 'string' },
          preferences: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                id: { type: 'string', format: 'uuid' },
                type: { type: 'string', enum: ['welcome', 'order', 'payment', 'system', 'promotional'] },
                channel: { type: 'string', enum: ['email', 'sms', 'in_app'] },
                enabled: { type: 'boolean' },
                frequency: { type: 'string', enum: ['immediate', 'daily', 'weekly', 'disabled'] },
                metadata: { type: 'object' },
                createdAt: { type: 'string', format: 'date-time' },
                updatedAt: { type: 'string', format: 'date-time' }
              }
            }
          }
        }
      },
      ErrorResponse: {
        type: 'object',
        properties: {
          error: { type: 'string', description: 'Error type or code' },
          message: { type: 'string', description: 'Human-readable error message' },
          timestamp: { type: 'string', format: 'date-time' },
          path: { type: 'string', description: 'Request path that caused the error' }
        }
      },
      ValidationErrorResponse: {
        type: 'object',
        properties: {
          error: { type: 'string', enum: ['validation_error'] },
          message: { type: 'string' },
          errors: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                field: { type: 'string' },
                message: { type: 'string' },
                value: { type: 'string' }
              }
            }
          },
          timestamp: { type: 'string', format: 'date-time' },
          path: { type: 'string' }
        }
      }
    }
  }
};

module.exports = swaggerJSDocs;