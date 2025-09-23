const { body, param, validationResult } = require('express-validator');

// Validation rules for cart operations
const cartValidationRules = {
  addItem: [
    body('product_id')
      .notEmpty()
      .withMessage('Product ID is required')
      .custom((value) => {
        // Accept both numeric and string product IDs
        if (typeof value === 'number' && Number.isInteger(value) && value > 0) {
          return true;
        }
        if (typeof value === 'string' && value.length >= 1 && value.length <= 100) {
          return true;
        }
        throw new Error('Product ID must be a positive integer or a string between 1 and 100 characters');
      }),

    body('quantity')
      .notEmpty()
      .withMessage('Quantity is required')
      .isInt({ min: 1, max: 10 })
      .withMessage('Quantity must be an integer between 1 and 10'),
  ],

  updateQuantity: [
    param('product_id')
      .notEmpty()
      .withMessage('Product ID is required')
      .custom((value) => {
        // Accept both numeric and string product IDs
        if (typeof value === 'string' && (value.length >= 1 && value.length <= 100)) {
          return true;
        }
        throw new Error('Product ID must be a string between 1 and 100 characters');
      }),

    body('quantity')
      .notEmpty()
      .withMessage('Quantity is required')
      .isInt({ min: 1, max: 10 })
      .withMessage('Quantity must be an integer between 1 and 10'),
  ],

  removeItem: [
    param('product_id')
      .notEmpty()
      .withMessage('Product ID is required')
      .custom((value) => {
        // Accept both numeric and string product IDs
        if (typeof value === 'string' && (value.length >= 1 && value.length <= 100)) {
          return true;
        }
        throw new Error('Product ID must be a string between 1 and 100 characters');
      }),
  ],
};

// Middleware to handle validation errors
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);

  if (!errors.isEmpty()) {
    const errorDetails = errors.array().map((error) => ({
      field: error.path || error.param,
      message: error.msg,
      value: error.value,
    }));

    return res.status(400).json({
      error: 'Validation failed',
      details: errorDetails,
      timestamp: new Date().toISOString(),
      correlation_id: req.correlationId,
    });
  }

  next();
};

// Combine validation rules with error handling
const createValidationChain = (rules) => {
  return [...rules, handleValidationErrors];
};

module.exports = {
  validateAddItem: createValidationChain(cartValidationRules.addItem),
  validateUpdateQuantity: createValidationChain(
    cartValidationRules.updateQuantity
  ),
  validateRemoveItem: createValidationChain(cartValidationRules.removeItem),
  handleValidationErrors,
};
