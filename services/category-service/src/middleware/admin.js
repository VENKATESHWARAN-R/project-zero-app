// Admin authorization middleware
const requireAdmin = (req, res, next) => {
  try {
    if (!req.user) {
      return res.status(401).json({
        error: {
          code: 'AUTHENTICATION_REQUIRED',
          message: 'Authentication required for admin operations',
        },
        timestamp: new Date().toISOString(),
        request_id: req.id,
      });
    }

    // Check if user has admin role
    if (!req.user.is_admin && req.user.role !== 'admin') {
      return res.status(403).json({
        error: {
          code: 'ADMIN_REQUIRED',
          message: 'Admin privileges required for this operation',
        },
        timestamp: new Date().toISOString(),
        request_id: req.id,
      });
    }

    next();
  } catch (error) {
    console.error('Admin middleware error:', error);
    return res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Internal authorization error',
      },
      timestamp: new Date().toISOString(),
      request_id: req.id,
    });
  }
};

module.exports = {
  requireAdmin,
};