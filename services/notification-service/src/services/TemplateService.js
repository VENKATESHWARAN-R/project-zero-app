const { NotificationTemplate } = require('../models');
const NotificationService = require('./NotificationService');

class TemplateService {
  constructor() {
    this.notificationService = new NotificationService();
  }

  /**
   * Create a new notification template
   */
  async createTemplate(templateData) {
    try {
      // Validate template name format
      const namePattern = /^[a-z]+_[a-z]+_[a-z_]+$/;
      if (!namePattern.test(templateData.name)) {
        throw new Error('Template name must follow pattern: type_channel_purpose (lowercase with underscores)');
      }

      // Validate name matches type and channel
      const expectedPrefix = `${templateData.type}_${templateData.channel}_`;
      if (!templateData.name.startsWith(expectedPrefix)) {
        throw new Error(`Template name must start with ${expectedPrefix}`);
      }

      // Check if template with this name already exists
      const existingTemplate = await NotificationTemplate.findOne({
        where: { name: templateData.name },
      });

      if (existingTemplate) {
        throw new Error(`Template with name '${templateData.name}' already exists`);
      }

      // Create the template
      const template = await NotificationTemplate.create({
        name: templateData.name,
        type: templateData.type,
        channel: templateData.channel,
        subject: templateData.subject,
        content: templateData.content,
        variables: templateData.variables || {},
        isActive: templateData.isActive !== undefined ? templateData.isActive : true,
      });

      return template;
    } catch (error) {
      console.error('Error creating template:', error);
      throw error;
    }
  }

  /**
   * Get template by ID
   */
  async getTemplateById(templateId) {
    try {
      const template = await NotificationTemplate.findByPk(templateId);
      if (!template) {
        throw new Error('Template not found');
      }
      return template;
    } catch (error) {
      console.error('Error getting template:', error);
      throw error;
    }
  }

  /**
   * Get template by name
   */
  async getTemplateByName(templateName) {
    try {
      const template = await NotificationTemplate.findByName(templateName);
      if (!template) {
        throw new Error(`Template '${templateName}' not found`);
      }
      return template;
    } catch (error) {
      console.error('Error getting template by name:', error);
      throw error;
    }
  }

  /**
   * Get all templates with filtering
   */
  async getTemplates(options = {}) {
    try {
      const { type, channel, active } = options;
      const whereClause = {};

      if (type) {
        whereClause.type = type;
      }
      if (channel) {
        whereClause.channel = channel;
      }
      if (active !== undefined) {
        whereClause.isActive = active;
      }

      const templates = await NotificationTemplate.findAll({
        where: whereClause,
        order: [['type', 'ASC'], ['channel', 'ASC'], ['name', 'ASC']],
      });

      return templates;
    } catch (error) {
      console.error('Error getting templates:', error);
      throw error;
    }
  }

  /**
   * Update an existing template
   */
  async updateTemplate(templateId, updateData) {
    try {
      const template = await NotificationTemplate.findByPk(templateId);
      if (!template) {
        throw new Error('Template not found');
      }

      // Validate update data
      const allowedFields = ['subject', 'content', 'variables', 'isActive'];
      const updateFields = {};

      for (const field of allowedFields) {
        if (updateData[field] !== undefined) {
          updateFields[field] = updateData[field];
        }
      }

      if (Object.keys(updateFields).length === 0) {
        throw new Error('No valid fields to update');
      }

      // Update the template
      await template.update(updateFields);

      return template;
    } catch (error) {
      console.error('Error updating template:', error);
      throw error;
    }
  }

  /**
   * Delete a template (soft delete by setting isActive to false)
   */
  async deleteTemplate(templateId) {
    try {
      const template = await NotificationTemplate.findByPk(templateId);
      if (!template) {
        throw new Error('Template not found');
      }

      await template.update({ isActive: false });
      return template;
    } catch (error) {
      console.error('Error deleting template:', error);
      throw error;
    }
  }

  /**
   * Render a template with variables
   */
  async renderTemplate(templateName, variables = {}) {
    try {
      const template = await this.getTemplateByName(templateName);
      return template.render(variables);
    } catch (error) {
      console.error('Error rendering template:', error);
      throw error;
    }
  }

  /**
   * Validate template variables
   */
  async validateTemplateVariables(templateName, variables = {}) {
    try {
      const template = await this.getTemplateByName(templateName);
      return template.validateVariables(variables);
    } catch (error) {
      console.error('Error validating template variables:', error);
      throw error;
    }
  }

  /**
   * Send notification using a template
   */
  async sendTemplateNotification(notificationData) {
    try {
      const { templateName, variables, userId, recipient, scheduledAt } = notificationData;

      // Get and validate template
      const template = await this.getTemplateByName(templateName);

      if (!template.isActive) {
        throw new Error(`Template '${templateName}' is not active`);
      }

      // Validate variables
      const validation = template.validateVariables(variables);
      if (!validation.valid) {
        throw new Error(validation.error);
      }

      // Render template
      const rendered = template.render(variables);

      // Determine recipient if not provided
      let finalRecipient = recipient;
      if (!finalRecipient) {
        // For email templates, we would need to get user's email from user service
        // For SMS, we would need user's phone number
        // For now, this is a placeholder - in real implementation we'd call user service
        if (template.channel === 'email') {
          finalRecipient = `${userId}@example.com`; // Placeholder
        } else if (template.channel === 'sms') {
          finalRecipient = `+1-555-${userId.slice(-7)}`; // Placeholder
        } else {
          finalRecipient = userId; // For in-app notifications
        }
      }

      // Create notification data
      const notificationPayload = {
        userId,
        templateId: template.id,
        channel: template.channel,
        recipient: finalRecipient,
        subject: rendered.subject,
        content: rendered.content,
        metadata: {
          templateName: template.name,
          type: template.type,
          variables,
          ...notificationData.metadata,
        },
        scheduledAt,
        priority: notificationData.priority,
      };

      // Create and send notification
      return await this.notificationService.createNotification(notificationPayload);
    } catch (error) {
      console.error('Error sending template notification:', error);
      throw error;
    }
  }

  /**
   * Get templates by type and channel
   */
  async getTemplatesByTypeAndChannel(type, channel) {
    try {
      return await NotificationTemplate.findByTypeAndChannel(type, channel);
    } catch (error) {
      console.error('Error getting templates by type and channel:', error);
      throw error;
    }
  }

  /**
   * Get active templates only
   */
  async getActiveTemplates() {
    try {
      return await NotificationTemplate.findActive();
    } catch (error) {
      console.error('Error getting active templates:', error);
      throw error;
    }
  }

  /**
   * Preview template rendering
   */
  async previewTemplate(templateName, variables = {}) {
    try {
      const template = await this.getTemplateByName(templateName);

      // Validate variables
      const validation = template.validateVariables(variables);
      if (!validation.valid) {
        return {
          valid: false,
          error: validation.error,
          preview: null,
        };
      }

      // Render template
      const rendered = template.render(variables);

      return {
        valid: true,
        error: null,
        preview: {
          subject: rendered.subject,
          content: rendered.content,
          channel: template.channel,
          type: template.type,
        },
      };
    } catch (error) {
      return {
        valid: false,
        error: error.message,
        preview: null,
      };
    }
  }

  /**
   * Clone an existing template
   */
  async cloneTemplate(templateId, newName, modifications = {}) {
    try {
      const sourceTemplate = await this.getTemplateById(templateId);

      // Prepare new template data
      const newTemplateData = {
        name: newName,
        type: sourceTemplate.type,
        channel: sourceTemplate.channel,
        subject: modifications.subject || sourceTemplate.subject,
        content: modifications.content || sourceTemplate.content,
        variables: modifications.variables || sourceTemplate.variables,
        isActive: modifications.isActive !== undefined ? modifications.isActive : sourceTemplate.isActive,
      };

      return await this.createTemplate(newTemplateData);
    } catch (error) {
      console.error('Error cloning template:', error);
      throw error;
    }
  }

  /**
   * Get template usage statistics
   */
  async getTemplateStats(templateId, timeRange = '30d') {
    try {
      const template = await this.getTemplateById(templateId);

      // Calculate time range
      const now = new Date();
      let startDate;
      switch (timeRange) {
        case '24h':
          startDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
          break;
        case '7d':
          startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          break;
        case '30d':
          startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          break;
        default:
          startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      }

      // Get notification stats for this template
      const { Notification } = require('../models');
      const stats = await Notification.findAll({
        where: {
          templateId: template.id,
          createdAt: {
            [Notification.sequelize.Op.gte]: startDate,
          },
        },
        attributes: [
          'status',
          [Notification.sequelize.fn('COUNT', '*'), 'count'],
        ],
        group: ['status'],
        raw: true,
      });

      // Format the results
      const result = {
        templateId: template.id,
        templateName: template.name,
        timeRange,
        startDate,
        endDate: now,
        total: 0,
        byStatus: {
          pending: 0,
          sent: 0,
          delivered: 0,
          failed: 0,
        },
      };

      stats.forEach(stat => {
        const count = parseInt(stat.count);
        result.total += count;
        result.byStatus[stat.status] = count;
      });

      // Calculate success rate
      result.successRate = result.total > 0 ?
        ((result.byStatus.sent + result.byStatus.delivered) / result.total * 100).toFixed(2) :
        0;

      return result;
    } catch (error) {
      console.error('Error getting template stats:', error);
      throw error;
    }
  }
}

module.exports = TemplateService;