const TemplateService = require('../services/TemplateService');

// Create service instance
const templateService = new TemplateService();

class TemplateController {
  static async getTemplates(req, res) {
    try {
      const { type, channel, active } = req.query;

      const filters = {};
      if (type) filters.type = type;
      if (channel) filters.channel = channel;
      if (active !== undefined) filters.isActive = active === 'true';

      const templates = await templateService.getTemplates(filters);

      res.status(200).json({
        templates
      });
    } catch (error) {
      console.error('Error getting templates:', error);
      res.status(500).json({
        error: 'internal_error',
        message: 'Failed to retrieve templates',
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }
  }

  static async createTemplate(req, res) {
    try {
      // Check if user has admin privileges
      if (!req.user.isAdmin) {
        return res.status(403).json({
          error: 'forbidden',
          message: 'Admin access required',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      const { name, type, channel, subject, content, variables, isActive = true } = req.body;

      if (!name || !type || !channel || !content) {
        return res.status(400).json({
          error: 'validation_error',
          message: 'Missing required fields: name, type, channel, content',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      // Validate name pattern
      const namePattern = /^[a-z]+_[a-z]+_[a-z_]+$/;
      if (!namePattern.test(name)) {
        return res.status(400).json({
          error: 'validation_error',
          message: 'Template name must follow pattern: type_channel_purpose (lowercase with underscores)',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      const template = await templateService.createTemplate({
        name,
        type,
        channel,
        subject,
        content,
        variables,
        isActive
      });

      res.status(201).json(template);
    } catch (error) {
      if (error.name === 'SequelizeUniqueConstraintError') {
        return res.status(400).json({
          error: 'validation_error',
          message: 'Template name already exists',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      console.error('Error creating template:', error);
      res.status(500).json({
        error: 'internal_error',
        message: 'Failed to create template',
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }
  }

  static async getTemplateById(req, res) {
    try {
      const { id } = req.params;

      const template = await templateService.getTemplateById(id);

      if (!template) {
        return res.status(404).json({
          error: 'not_found',
          message: 'Template not found',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      res.status(200).json(template);
    } catch (error) {
      console.error('Error getting template:', error);
      res.status(500).json({
        error: 'internal_error',
        message: 'Failed to retrieve template',
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }
  }

  static async updateTemplate(req, res) {
    try {
      // Check if user has admin privileges
      if (!req.user.isAdmin) {
        return res.status(403).json({
          error: 'forbidden',
          message: 'Admin access required',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      const { id } = req.params;
      const { subject, content, variables, isActive } = req.body;

      const template = await templateService.getTemplateById(id);

      if (!template) {
        return res.status(404).json({
          error: 'not_found',
          message: 'Template not found',
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      const updateData = {};
      if (subject !== undefined) updateData.subject = subject;
      if (content !== undefined) updateData.content = content;
      if (variables !== undefined) updateData.variables = variables;
      if (isActive !== undefined) updateData.isActive = isActive;

      const updatedTemplate = await templateService.updateTemplate(id, updateData);

      res.status(200).json(updatedTemplate);
    } catch (error) {
      console.error('Error updating template:', error);
      res.status(500).json({
        error: 'internal_error',
        message: 'Failed to update template',
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }
  }
}

module.exports = TemplateController;