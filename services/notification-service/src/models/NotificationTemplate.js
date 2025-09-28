const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const NotificationTemplate = sequelize.define('NotificationTemplate', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
  },
  name: {
    type: DataTypes.STRING(255),
    allowNull: false,
    unique: true,
    validate: {
      notEmpty: true,
      isValidName(value) {
        // Template name must follow pattern: {type}_{channel}_{purpose}
        const namePattern = /^[a-z]+_[a-z]+_[a-z_]+$/;
        if (!namePattern.test(value)) {
          throw new Error('Template name must follow pattern: type_channel_purpose (lowercase with underscores)');
        }
      },
    },
  },
  type: {
    type: DataTypes.ENUM('welcome', 'order', 'payment', 'system', 'promotional'),
    allowNull: false,
    validate: {
      isIn: [['welcome', 'order', 'payment', 'system', 'promotional']],
    },
  },
  channel: {
    type: DataTypes.ENUM('email', 'sms', 'in_app'),
    allowNull: false,
    validate: {
      isIn: [['email', 'sms', 'in_app']],
    },
  },
  subject: {
    type: DataTypes.STRING(500),
    allowNull: true,
    validate: {
      isRequiredForEmail(value) {
        if (this.channel === 'email' && (!value || value.trim() === '')) {
          throw new Error('Subject is required for email templates');
        }
      },
    },
  },
  content: {
    type: DataTypes.TEXT,
    allowNull: false,
    validate: {
      notEmpty: true,
      hasValidVariables(value) {
        // Check for unclosed template variables
        const openBraces = (value.match(/{{/g) || []).length;
        const closeBraces = (value.match(/}}/g) || []).length;
        if (openBraces !== closeBraces) {
          throw new Error('Template has unclosed variable placeholders');
        }
      },
    },
  },
  variables: {
    type: DataTypes.JSON,
    allowNull: true,
    defaultValue: {},
    validate: {
      isValidVariableSchema(value) {
        if (value && typeof value === 'object') {
          for (const [key, schema] of Object.entries(value)) {
            if (!schema.type || !['string', 'number', 'boolean', 'object', 'array'].includes(schema.type)) {
              throw new Error(`Invalid variable type for ${key}. Must be one of: string, number, boolean, object, array`);
            }
          }
        }
      },
    },
  },
  isActive: {
    type: DataTypes.BOOLEAN,
    allowNull: false,
    defaultValue: true,
  },
}, {
  tableName: 'notification_templates',
  indexes: [
    {
      fields: ['type', 'channel'],
      name: 'idx_notification_templates_type_channel',
    },
    {
      fields: ['isActive'],
      name: 'idx_notification_templates_active',
    },
  ],
  validate: {
    nameMatchesTypeAndChannel() {
      if (this.name && this.type && this.channel) {
        const expectedPrefix = `${this.type}_${this.channel}_`;
        if (!this.name.startsWith(expectedPrefix)) {
          throw new Error(`Template name must start with ${expectedPrefix}`);
        }
      }
    },
  },
});

// Instance methods
NotificationTemplate.prototype.render = function(variables = {}) {
  if (!this.isActive) {
    throw new Error('Cannot render inactive template');
  }

  // Validate required variables
  if (this.variables) {
    for (const [varName, schema] of Object.entries(this.variables)) {
      if (schema.required && !(varName in variables)) {
        throw new Error(`Required variable '${varName}' is missing`);
      }
    }
  }

  // Replace variables in content
  let renderedContent = this.content;
  for (const [key, value] of Object.entries(variables)) {
    const placeholder = new RegExp(`{{\\s*${key}\\s*}}`, 'g');
    renderedContent = renderedContent.replace(placeholder, String(value));
  }

  // Replace variables in subject if it exists
  let renderedSubject = this.subject;
  if (renderedSubject) {
    for (const [key, value] of Object.entries(variables)) {
      const placeholder = new RegExp(`{{\\s*${key}\\s*}}`, 'g');
      renderedSubject = renderedSubject.replace(placeholder, String(value));
    }
  }

  // Check for unreplaced variables
  const unreplacedVars = renderedContent.match(/{{[^}]+}}/g);
  if (unreplacedVars) {
    throw new Error(`Unresolved template variables: ${unreplacedVars.join(', ')}`);
  }

  return {
    subject: renderedSubject,
    content: renderedContent,
  };
};

NotificationTemplate.prototype.validateVariables = function(variables) {
  if (!this.variables) return true;

  for (const [varName, schema] of Object.entries(this.variables)) {
    if (schema.required && !(varName in variables)) {
      return { valid: false, error: `Required variable '${varName}' is missing` };
    }

    if (varName in variables) {
      const value = variables[varName];
      const expectedType = schema.type;

      // Type validation
      if (expectedType === 'string' && typeof value !== 'string') {
        return { valid: false, error: `Variable '${varName}' must be a string` };
      }
      if (expectedType === 'number' && typeof value !== 'number') {
        return { valid: false, error: `Variable '${varName}' must be a number` };
      }
      if (expectedType === 'boolean' && typeof value !== 'boolean') {
        return { valid: false, error: `Variable '${varName}' must be a boolean` };
      }
      if (expectedType === 'object' && (typeof value !== 'object' || Array.isArray(value))) {
        return { valid: false, error: `Variable '${varName}' must be an object` };
      }
      if (expectedType === 'array' && !Array.isArray(value)) {
        return { valid: false, error: `Variable '${varName}' must be an array` };
      }
    }
  }

  return { valid: true };
};

// Class methods
NotificationTemplate.findByName = function(name) {
  return this.findOne({ where: { name, isActive: true } });
};

NotificationTemplate.findByTypeAndChannel = function(type, channel, options = {}) {
  return this.findAll({
    where: { type, channel, isActive: true },
    order: [['name', 'ASC']],
    ...options,
  });
};

NotificationTemplate.findActive = function(options = {}) {
  return this.findAll({
    where: { isActive: true },
    order: [['type', 'ASC'], ['channel', 'ASC'], ['name', 'ASC']],
    ...options,
  });
};

module.exports = NotificationTemplate;