const validationMiddleware = {
  validateSendNotificationRequest: (req, res, next) => {
    const { userId, channel, recipient, content } = req.body;
    const errors = [];

    if (!userId || typeof userId !== 'string') {
      errors.push({ field: 'userId', message: 'User ID is required and must be a string', value: userId });
    }

    if (!channel || !['email', 'sms', 'in_app'].includes(channel)) {
      errors.push({ field: 'channel', message: 'Channel must be one of: email, sms, in_app', value: channel });
    }

    if (!recipient || typeof recipient !== 'string') {
      errors.push({ field: 'recipient', message: 'Recipient is required and must be a string', value: recipient });
    } else {
      // Validate recipient format based on channel
      if (channel === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(recipient)) {
          errors.push({ field: 'recipient', message: 'Invalid email format', value: recipient });
        }
      } else if (channel === 'sms') {
        const phoneRegex = /^\+?[\d\s\-\(\)]+$/;
        if (!phoneRegex.test(recipient)) {
          errors.push({ field: 'recipient', message: 'Invalid phone number format', value: recipient });
        }
      }
    }

    if (!content || typeof content !== 'string' || content.trim().length === 0) {
      errors.push({ field: 'content', message: 'Content is required and cannot be empty', value: content });
    }

    if (req.body.subject && typeof req.body.subject !== 'string') {
      errors.push({ field: 'subject', message: 'Subject must be a string', value: req.body.subject });
    }

    if (req.body.priority && !['low', 'normal', 'high'].includes(req.body.priority)) {
      errors.push({ field: 'priority', message: 'Priority must be one of: low, normal, high', value: req.body.priority });
    }

    if (errors.length > 0) {
      return res.status(422).json({
        error: 'validation_error',
        message: 'Request validation failed',
        errors,
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }

    next();
  },

  validateScheduleNotificationRequest: (req, res, next) => {
    const { scheduledAt } = req.body;
    const errors = [];

    // First validate basic notification fields
    validationMiddleware.validateSendNotificationRequest(req, res, (validationError) => {
      if (validationError) return; // Validation failed, response already sent

      // Validate schedule-specific fields
      if (!scheduledAt) {
        errors.push({ field: 'scheduledAt', message: 'Scheduled time is required', value: scheduledAt });
      } else {
        const scheduledDate = new Date(scheduledAt);
        if (isNaN(scheduledDate.getTime())) {
          errors.push({ field: 'scheduledAt', message: 'Invalid date format', value: scheduledAt });
        } else if (scheduledDate <= new Date()) {
          errors.push({ field: 'scheduledAt', message: 'Scheduled time must be in the future', value: scheduledAt });
        }
      }

      if (req.body.maxAttempts && (!Number.isInteger(req.body.maxAttempts) || req.body.maxAttempts < 1 || req.body.maxAttempts > 10)) {
        errors.push({ field: 'maxAttempts', message: 'Max attempts must be an integer between 1 and 10', value: req.body.maxAttempts });
      }

      if (req.body.retryInterval && (!Number.isInteger(req.body.retryInterval) || req.body.retryInterval < 60)) {
        errors.push({ field: 'retryInterval', message: 'Retry interval must be an integer >= 60 seconds', value: req.body.retryInterval });
      }

      if (errors.length > 0) {
        return res.status(422).json({
          error: 'validation_error',
          message: 'Request validation failed',
          errors,
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      next();
    });
  },

  validateTemplateNotificationRequest: (req, res, next) => {
    const { userId, templateName, variables } = req.body;
    const errors = [];

    if (!userId || typeof userId !== 'string') {
      errors.push({ field: 'userId', message: 'User ID is required and must be a string', value: userId });
    }

    if (!templateName || typeof templateName !== 'string') {
      errors.push({ field: 'templateName', message: 'Template name is required and must be a string', value: templateName });
    }

    if (!variables || typeof variables !== 'object' || Array.isArray(variables)) {
      errors.push({ field: 'variables', message: 'Variables must be an object', value: variables });
    }

    if (req.body.recipient && typeof req.body.recipient !== 'string') {
      errors.push({ field: 'recipient', message: 'Recipient must be a string', value: req.body.recipient });
    }

    if (req.body.scheduledAt) {
      const scheduledDate = new Date(req.body.scheduledAt);
      if (isNaN(scheduledDate.getTime())) {
        errors.push({ field: 'scheduledAt', message: 'Invalid date format', value: req.body.scheduledAt });
      } else if (scheduledDate <= new Date()) {
        errors.push({ field: 'scheduledAt', message: 'Scheduled time must be in the future', value: req.body.scheduledAt });
      }
    }

    if (errors.length > 0) {
      return res.status(422).json({
        error: 'validation_error',
        message: 'Request validation failed',
        errors,
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }

    next();
  },

  validateCreateTemplateRequest: (req, res, next) => {
    const { name, type, channel, content } = req.body;
    const errors = [];

    if (!name || typeof name !== 'string') {
      errors.push({ field: 'name', message: 'Name is required and must be a string', value: name });
    } else {
      const namePattern = /^[a-z]+_[a-z]+_[a-z_]+$/;
      if (!namePattern.test(name)) {
        errors.push({ field: 'name', message: 'Name must follow pattern: type_channel_purpose (lowercase with underscores)', value: name });
      }
    }

    if (!type || !['welcome', 'order', 'payment', 'system', 'promotional'].includes(type)) {
      errors.push({ field: 'type', message: 'Type must be one of: welcome, order, payment, system, promotional', value: type });
    }

    if (!channel || !['email', 'sms', 'in_app'].includes(channel)) {
      errors.push({ field: 'channel', message: 'Channel must be one of: email, sms, in_app', value: channel });
    }

    if (!content || typeof content !== 'string' || content.trim().length === 0) {
      errors.push({ field: 'content', message: 'Content is required and cannot be empty', value: content });
    }

    if (req.body.subject && (typeof req.body.subject !== 'string' || req.body.subject.length > 500)) {
      errors.push({ field: 'subject', message: 'Subject must be a string with maximum 500 characters', value: req.body.subject });
    }

    if (req.body.variables && (typeof req.body.variables !== 'object' || Array.isArray(req.body.variables))) {
      errors.push({ field: 'variables', message: 'Variables must be an object', value: req.body.variables });
    }

    if (req.body.isActive !== undefined && typeof req.body.isActive !== 'boolean') {
      errors.push({ field: 'isActive', message: 'isActive must be a boolean', value: req.body.isActive });
    }

    if (errors.length > 0) {
      return res.status(422).json({
        error: 'validation_error',
        message: 'Request validation failed',
        errors,
        timestamp: new Date().toISOString(),
        path: req.path
      });
    }

    next();
  },

  validateUUID: (paramName) => {
    return (req, res, next) => {
      const value = req.params[paramName];
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

      if (!uuidRegex.test(value)) {
        return res.status(400).json({
          error: 'validation_error',
          message: `Invalid UUID format for ${paramName}`,
          timestamp: new Date().toISOString(),
          path: req.path
        });
      }

      next();
    };
  }
};

module.exports = validationMiddleware;