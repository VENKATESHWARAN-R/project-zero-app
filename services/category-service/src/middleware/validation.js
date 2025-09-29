const { body, param, query, validationResult } = require('express-validator');

// Validation error handler
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Request validation failed',
        details: errors.array().map(err => ({
          field: err.path,
          message: err.msg,
          value: err.value,
        })),
      },
      timestamp: new Date().toISOString(),
      request_id: req.id,
    });
  }
  next();
};

// Category validation rules
const categoryValidation = {
  create: [
    body('name')
      .isLength({ min: 1, max: 100 })
      .withMessage('Name must be between 1 and 100 characters')
      .trim(),
    body('description')
      .optional()
      .isLength({ max: 1000 })
      .withMessage('Description must not exceed 1000 characters')
      .trim(),
    body('image_url')
      .optional()
      .isURL()
      .withMessage('Image URL must be a valid URL'),
    body('parent_id')
      .optional()
      .isInt({ min: 1 })
      .withMessage('Parent ID must be a positive integer'),
    body('sort_order')
      .optional()
      .isInt({ min: 0 })
      .withMessage('Sort order must be a non-negative integer'),
    body('metadata')
      .optional()
      .isObject()
      .withMessage('Metadata must be a valid JSON object'),
    handleValidationErrors,
  ],

  update: [
    param('id')
      .isInt({ min: 1 })
      .withMessage('Category ID must be a positive integer'),
    body('name')
      .optional()
      .isLength({ min: 1, max: 100 })
      .withMessage('Name must be between 1 and 100 characters')
      .trim(),
    body('description')
      .optional()
      .isLength({ max: 1000 })
      .withMessage('Description must not exceed 1000 characters')
      .trim(),
    body('image_url')
      .optional()
      .custom((value) => {
        if (value === null) return true; // Allow null to clear image
        if (typeof value === 'string' && value.length === 0) return true; // Allow empty string
        return /^https?:\/\/.+/.test(value); // Validate URL
      })
      .withMessage('Image URL must be a valid URL'),
    body('parent_id')
      .optional()
      .custom((value) => {
        if (value === null) return true; // Allow null for root category
        return Number.isInteger(value) && value > 0;
      })
      .withMessage('Parent ID must be a positive integer or null'),
    body('sort_order')
      .optional()
      .isInt({ min: 0 })
      .withMessage('Sort order must be a non-negative integer'),
    body('is_active')
      .optional()
      .isBoolean()
      .withMessage('is_active must be a boolean'),
    body('metadata')
      .optional()
      .custom((value) => {
        if (value === null) return true; // Allow null
        return typeof value === 'object' && !Array.isArray(value);
      })
      .withMessage('Metadata must be a valid JSON object or null'),
    handleValidationErrors,
  ],

  getById: [
    param('id')
      .isInt({ min: 1 })
      .withMessage('Category ID must be a positive integer'),
    query('include_children')
      .optional()
      .isBoolean()
      .withMessage('include_children must be a boolean'),
    query('include_ancestors')
      .optional()
      .isBoolean()
      .withMessage('include_ancestors must be a boolean'),
    query('include_product_count')
      .optional()
      .isBoolean()
      .withMessage('include_product_count must be a boolean'),
    handleValidationErrors,
  ],

  delete: [
    param('id')
      .isInt({ min: 1 })
      .withMessage('Category ID must be a positive integer'),
    query('force')
      .optional()
      .isBoolean()
      .withMessage('force must be a boolean'),
    handleValidationErrors,
  ],

  list: [
    query('parent_id')
      .optional()
      .custom((value) => {
        if (value === 'null' || value === null) return true; // Allow null string
        return Number.isInteger(parseInt(value)) && parseInt(value) > 0;
      })
      .withMessage('parent_id must be a positive integer or null'),
    query('include_children')
      .optional()
      .isBoolean()
      .withMessage('include_children must be a boolean'),
    query('include_product_count')
      .optional()
      .isBoolean()
      .withMessage('include_product_count must be a boolean'),
    query('active_only')
      .optional()
      .isBoolean()
      .withMessage('active_only must be a boolean'),
    handleValidationErrors,
  ],

  search: [
    query('q')
      .isLength({ min: 1 })
      .withMessage('Search query is required and must not be empty')
      .trim(),
    query('active_only')
      .optional()
      .isBoolean()
      .withMessage('active_only must be a boolean'),
    handleValidationErrors,
  ],

  products: [
    param('id')
      .isInt({ min: 1 })
      .withMessage('Category ID must be a positive integer'),
    query('include_subcategories')
      .optional()
      .isBoolean()
      .withMessage('include_subcategories must be a boolean'),
    query('page')
      .optional()
      .isInt({ min: 1 })
      .withMessage('page must be a positive integer'),
    query('limit')
      .optional()
      .isInt({ min: 1, max: 100 })
      .withMessage('limit must be between 1 and 100'),
    handleValidationErrors,
  ],
};

module.exports = {
  categoryValidation,
  handleValidationErrors,
};