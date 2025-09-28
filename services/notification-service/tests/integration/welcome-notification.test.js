const request = require('supertest');
const app = require('../../src/app');
const { initializeDatabase } = require('../../src/models');

describe('Welcome Notification Integration Test', () => {
  let validJWT;
  const testUserId = 'user123';

  beforeAll(async() => {
    // Initialize database with associations and seeding
    await initializeDatabase({ force: true });

    // Mock JWT token - in real implementation this would come from auth service
    validJWT = 'Bearer test-jwt-token';
  });

  describe('User Registration Welcome Flow', () => {
    it('should send welcome notification using template', async() => {
      const welcomeRequest = {
        userId: testUserId,
        templateName: 'welcome_email_registration',
        variables: {
          userName: 'John Doe',
          activationLink: 'https://app.example.com/activate/abc123',
        },
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(welcomeRequest)
        .expect(201);

      // Verify notification was created
      expect(response.body).toMatchObject({
        id: expect.toBeValidUUID(),
        userId: testUserId,
        channel: 'email',
        status: expect.stringMatching(/^(pending|sent|delivered)$/),
        templateId: expect.toBeValidUUID(),
        content: expect.stringContaining('John Doe'),
        content: expect.stringContaining('https://app.example.com/activate/abc123'),
      });

      const notificationId = response.body.id;

      // Verify notification appears in user's history
      const historyResponse = await request(app)
        .get('/notifications')
        .set('Authorization', validJWT)
        .expect(200);

      expect(historyResponse.body.notifications).toContainEqual(
        expect.objectContaining({
          id: notificationId,
          userId: testUserId,
        })
      );

      // Verify notification details can be retrieved
      const detailResponse = await request(app)
        .get(`/notifications/${notificationId}`)
        .set('Authorization', validJWT)
        .expect(200);

      expect(detailResponse.body).toMatchObject({
        id: notificationId,
        userId: testUserId,
        channel: 'email',
        content: expect.stringContaining('John Doe'),
      });
    });

    it('should handle welcome notification with custom recipient', async() => {
      const welcomeRequest = {
        userId: testUserId,
        templateName: 'welcome_email_registration',
        variables: {
          userName: 'Jane Smith',
          activationLink: 'https://app.example.com/activate/def456',
        },
        recipient: 'jane.custom@example.com',
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(welcomeRequest)
        .expect(201);

      expect(response.body).toMatchObject({
        userId: testUserId,
        recipient: 'jane.custom@example.com',
        content: expect.stringContaining('Jane Smith'),
      });
    });

    it('should validate template variables are properly substituted', async() => {
      const welcomeRequest = {
        userId: testUserId,
        templateName: 'welcome_email_registration',
        variables: {
          userName: 'Test User',
          activationLink: 'https://app.example.com/activate/xyz789',
        },
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(welcomeRequest)
        .expect(201);

      // Verify all template variables were substituted
      expect(response.body.content).toContain('Test User');
      expect(response.body.content).toContain('https://app.example.com/activate/xyz789');

      // Verify no template placeholders remain
      expect(response.body.content).not.toMatch(/{{.*}}/);
    });

    it('should fail gracefully with missing template variables', async() => {
      const welcomeRequest = {
        userId: testUserId,
        templateName: 'welcome_email_registration',
        variables: {
          userName: 'Incomplete User',
          // Missing activationLink
        },
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(welcomeRequest)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('variable'),
      });
    });

    it('should track notification delivery status', async() => {
      const welcomeRequest = {
        userId: testUserId,
        templateName: 'welcome_email_registration',
        variables: {
          userName: 'Status Test User',
          activationLink: 'https://app.example.com/activate/status123',
        },
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(welcomeRequest)
        .expect(201);

      const notificationId = response.body.id;

      // Wait for mock delivery simulation
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Check notification status has been updated
      const statusResponse = await request(app)
        .get(`/notifications/${notificationId}`)
        .set('Authorization', validJWT)
        .expect(200);

      expect(statusResponse.body.status).toMatch(/^(sent|delivered|failed)$/);

      if (statusResponse.body.status === 'sent' || statusResponse.body.status === 'delivered') {
        expect(statusResponse.body.sentAt).toBeDefined();
        expect(new Date(statusResponse.body.sentAt)).toBeInstanceOf(Date);
      }

      if (statusResponse.body.status === 'delivered') {
        expect(statusResponse.body.deliveredAt).toBeDefined();
        expect(new Date(statusResponse.body.deliveredAt)).toBeInstanceOf(Date);
      }
    });

    it('should respect user notification preferences', async() => {
      // First, disable email notifications for welcome type
      const preferencesRequest = {
        preferences: [
          {
            type: 'welcome',
            channel: 'email',
            enabled: false,
            frequency: 'disabled',
          },
        ],
      };

      await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send(preferencesRequest)
        .expect(200);

      // Try to send welcome notification
      const welcomeRequest = {
        userId: testUserId,
        templateName: 'welcome_email_registration',
        variables: {
          userName: 'Blocked User',
          activationLink: 'https://app.example.com/activate/blocked',
        },
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(welcomeRequest)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('disabled'),
      });

      // Re-enable preferences for other tests
      const enableRequest = {
        preferences: [
          {
            type: 'welcome',
            channel: 'email',
            enabled: true,
            frequency: 'immediate',
          },
        ],
      };

      await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send(enableRequest)
        .expect(200);
    });

    it('should handle concurrent welcome notifications', async() => {
      const welcomeRequests = Array.from({ length: 5 }, (_, i) => ({
        userId: `concurrent-user-${i}`,
        templateName: 'welcome_email_registration',
        variables: {
          userName: `Concurrent User ${i}`,
          activationLink: `https://app.example.com/activate/concurrent${i}`,
        },
      }));

      // Send all notifications concurrently
      const promises = welcomeRequests.map(request =>
        request(app)
          .post('/notifications/template')
          .set('Authorization', validJWT)
          .send(request)
      );

      const responses = await Promise.all(promises);

      // All should succeed
      responses.forEach(response => {
        expect(response.status).toBe(201);
        expect(response.body.id).toBeValidUUID();
      });

      // All should have unique IDs
      const ids = responses.map(r => r.body.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });
  });
});