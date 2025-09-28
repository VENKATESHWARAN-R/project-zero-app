const express = require('express');
const HealthController = require('../controllers/HealthController');
const NotificationController = require('../controllers/NotificationController');
const TemplateController = require('../controllers/TemplateController');
const PreferenceController = require('../controllers/PreferenceController');
const authMiddleware = require('../middleware/auth');
const validation = require('../middleware/validation');

const router = express.Router();

// Health endpoints (no authentication required)
router.get('/health', HealthController.health);
router.get('/health/ready', HealthController.ready);

// Notification endpoints (authentication required)
router.post('/notifications',
  authMiddleware,
  validation.validateSendNotificationRequest,
  NotificationController.sendNotification
);

router.get('/notifications',
  authMiddleware,
  NotificationController.getNotifications
);

router.get('/notifications/:id',
  authMiddleware,
  validation.validateUUID('id'),
  NotificationController.getNotificationById
);

router.post('/notifications/schedule',
  authMiddleware,
  validation.validateScheduleNotificationRequest,
  NotificationController.scheduleNotification
);

router.post('/notifications/template',
  authMiddleware,
  validation.validateTemplateNotificationRequest,
  NotificationController.sendTemplateNotification
);

// Template endpoints (authentication required)
router.get('/templates',
  authMiddleware,
  TemplateController.getTemplates
);

router.post('/templates',
  authMiddleware,
  validation.validateCreateTemplateRequest,
  TemplateController.createTemplate
);

router.get('/templates/:id',
  authMiddleware,
  validation.validateUUID('id'),
  TemplateController.getTemplateById
);

router.put('/templates/:id',
  authMiddleware,
  validation.validateUUID('id'),
  TemplateController.updateTemplate
);

// Preference endpoints (authentication required)
router.get('/preferences',
  authMiddleware,
  PreferenceController.getPreferences
);

router.put('/preferences',
  authMiddleware,
  PreferenceController.updatePreferences
);

module.exports = router;