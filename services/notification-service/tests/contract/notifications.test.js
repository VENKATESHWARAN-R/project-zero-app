const request = require('supertest');
const app = require('../../src/app');

describe('Notification Endpoints Contract Tests', () => {
  const validJWT = 'Bearer valid-jwt-token'; // Mock JWT for testing
  const validNotificationId = '123e4567-e89b-12d3-a456-426614174000';

  describe('POST /notifications', () => {
    const validNotificationRequest = {
      userId: 'user123',
      channel: 'email',
      recipient: 'test@example.com',
      subject: 'Test Subject',
      content: 'Test notification content',
      metadata: { orderId: 'order-123' },
      priority: 'normal',
    };

    it('should return 201 with notification response for valid request', async() => {
      const response = await request(app)
        .post('/notifications')
        .set('Authorization', validJWT)
        .send(validNotificationRequest)
        .expect(201);

      expect(response.body).toMatchObject({
        id: expect.toBeValidUUID(),
        userId: 'user123',
        channel: 'email',
        recipient: 'test@example.com',
        subject: 'Test Subject',
        content: 'Test notification content',
        metadata: { orderId: 'order-123' },
        status: expect.stringMatching(/^(pending|sent|delivered|failed)$/),
        createdAt: expect.any(String),
        updatedAt: expect.any(String),
      });
    });

    it('should return 401 for missing authorization', async() => {
      const response = await request(app)
        .post('/notifications')
        .send(validNotificationRequest)
        .expect(401);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
        timestamp: expect.any(String),
        path: '/notifications',
      });
    });

    it('should return 422 for missing required fields', async() => {
      const invalidRequest = { userId: 'user123' };

      const response = await request(app)
        .post('/notifications')
        .set('Authorization', validJWT)
        .send(invalidRequest)
        .expect(422);

      expect(response.body).toMatchObject({
        error: 'validation_error',
        message: expect.any(String),
        errors: expect.arrayContaining([
          expect.objectContaining({
            field: expect.any(String),
            message: expect.any(String),
          }),
        ]),
        timestamp: expect.any(String),
        path: '/notifications',
      });
    });

    it('should return 400 for invalid channel', async() => {
      const invalidRequest = {
        ...validNotificationRequest,
        channel: 'invalid-channel',
      };

      const response = await request(app)
        .post('/notifications')
        .set('Authorization', validJWT)
        .send(invalidRequest)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
      });
    });
  });

  describe('GET /notifications', () => {
    it('should return 200 with paginated notification history', async() => {
      const response = await request(app)
        .get('/notifications?page=1&limit=10')
        .set('Authorization', validJWT)
        .expect(200);

      expect(response.body).toMatchObject({
        notifications: expect.any(Array),
        pagination: {
          page: 1,
          limit: 10,
          totalPages: expect.any(Number),
          totalCount: expect.any(Number),
          hasNext: expect.any(Boolean),
          hasPrevious: expect.any(Boolean),
        },
      });
    });

    it('should return 401 for missing authorization', async() => {
      const response = await request(app)
        .get('/notifications')
        .expect(401);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
      });
    });

    it('should support filtering by channel', async() => {
      const response = await request(app)
        .get('/notifications?channel=email')
        .set('Authorization', validJWT)
        .expect(200);

      expect(response.body).toMatchObject({
        notifications: expect.any(Array),
        pagination: expect.any(Object),
      });
    });

    it('should support filtering by status', async() => {
      const response = await request(app)
        .get('/notifications?status=sent')
        .set('Authorization', validJWT)
        .expect(200);

      expect(response.body).toMatchObject({
        notifications: expect.any(Array),
        pagination: expect.any(Object),
      });
    });

    it('should support date range filtering', async() => {
      const startDate = '2025-01-01T00:00:00Z';
      const endDate = '2025-12-31T23:59:59Z';

      const response = await request(app)
        .get(`/notifications?startDate=${startDate}&endDate=${endDate}`)
        .set('Authorization', validJWT)
        .expect(200);

      expect(response.body).toMatchObject({
        notifications: expect.any(Array),
        pagination: expect.any(Object),
      });
    });
  });

  describe('GET /notifications/:id', () => {
    it('should return 200 with notification details for valid ID', async() => {
      const response = await request(app)
        .get(`/notifications/${validNotificationId}`)
        .set('Authorization', validJWT)
        .expect(200);

      expect(response.body).toMatchObject({
        id: validNotificationId,
        userId: expect.any(String),
        channel: expect.stringMatching(/^(email|sms|in_app)$/),
        recipient: expect.any(String),
        content: expect.any(String),
        status: expect.stringMatching(/^(pending|sent|delivered|failed)$/),
        createdAt: expect.any(String),
        updatedAt: expect.any(String),
      });
    });

    it('should return 401 for missing authorization', async() => {
      const response = await request(app)
        .get(`/notifications/${validNotificationId}`)
        .expect(401);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
      });
    });

    it('should return 404 for non-existent notification', async() => {
      const nonExistentId = '999e4567-e89b-12d3-a456-426614174999';

      const response = await request(app)
        .get(`/notifications/${nonExistentId}`)
        .set('Authorization', validJWT)
        .expect(404);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
        path: `/notifications/${nonExistentId}`,
      });
    });

    it('should return 400 for invalid UUID format', async() => {
      const invalidId = 'invalid-uuid';

      const response = await request(app)
        .get(`/notifications/${invalidId}`)
        .set('Authorization', validJWT)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
      });
    });
  });

  describe('POST /notifications/schedule', () => {
    const validScheduleRequest = {
      userId: 'user123',
      channel: 'email',
      recipient: 'test@example.com',
      subject: 'Scheduled Subject',
      content: 'Scheduled notification content',
      scheduledAt: '2025-10-01T10:00:00Z',
      maxAttempts: 3,
      retryInterval: 300,
    };

    it('should return 201 with scheduled notification response', async() => {
      const response = await request(app)
        .post('/notifications/schedule')
        .set('Authorization', validJWT)
        .send(validScheduleRequest)
        .expect(201);

      expect(response.body).toMatchObject({
        id: expect.toBeValidUUID(),
        scheduleId: expect.toBeValidUUID(),
        userId: 'user123',
        channel: 'email',
        recipient: 'test@example.com',
        content: 'Scheduled notification content',
        status: 'pending',
        scheduledAt: '2025-10-01T10:00:00.000Z',
        attempts: 0,
        maxAttempts: 3,
        createdAt: expect.any(String),
        updatedAt: expect.any(String),
      });
    });

    it('should return 401 for missing authorization', async() => {
      const response = await request(app)
        .post('/notifications/schedule')
        .send(validScheduleRequest)
        .expect(401);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
      });
    });

    it('should return 400 for past scheduled date', async() => {
      const pastRequest = {
        ...validScheduleRequest,
        scheduledAt: '2020-01-01T00:00:00Z',
      };

      const response = await request(app)
        .post('/notifications/schedule')
        .set('Authorization', validJWT)
        .send(pastRequest)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('future'),
      });
    });
  });

  describe('POST /notifications/template', () => {
    const validTemplateRequest = {
      userId: 'user123',
      templateName: 'welcome_email_registration',
      variables: {
        userName: 'John Doe',
        activationLink: 'https://app.example.com/activate/abc123',
      },
    };

    it('should return 201 with template notification response', async() => {
      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(validTemplateRequest)
        .expect(201);

      expect(response.body).toMatchObject({
        id: expect.toBeValidUUID(),
        userId: 'user123',
        templateId: expect.toBeValidUUID(),
        channel: expect.stringMatching(/^(email|sms|in_app)$/),
        recipient: expect.any(String),
        content: expect.stringContaining('John Doe'),
        status: expect.stringMatching(/^(pending|sent|delivered|failed)$/),
        createdAt: expect.any(String),
        updatedAt: expect.any(String),
      });
    });

    it('should return 401 for missing authorization', async() => {
      const response = await request(app)
        .post('/notifications/template')
        .send(validTemplateRequest)
        .expect(401);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
      });
    });

    it('should return 404 for non-existent template', async() => {
      const invalidRequest = {
        ...validTemplateRequest,
        templateName: 'nonexistent_template',
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(invalidRequest)
        .expect(404);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('template'),
      });
    });

    it('should support optional recipient override', async() => {
      const requestWithRecipient = {
        ...validTemplateRequest,
        recipient: 'custom@example.com',
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(requestWithRecipient)
        .expect(201);

      expect(response.body.recipient).toBe('custom@example.com');
    });

    it('should support optional scheduling', async() => {
      const scheduledRequest = {
        ...validTemplateRequest,
        scheduledAt: '2025-10-01T10:00:00Z',
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(scheduledRequest)
        .expect(201);

      expect(response.body.scheduledAt).toBe('2025-10-01T10:00:00.000Z');
    });
  });
});