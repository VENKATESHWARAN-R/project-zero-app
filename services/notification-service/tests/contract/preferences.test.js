const request = require('supertest');
const app = require('../../src/app');

describe('Preferences Endpoints Contract Tests', () => {
  const validJWT = 'Bearer valid-jwt-token'; // Mock JWT for testing

  describe('GET /preferences', () => {
    it('should return 200 with user preferences', async() => {
      const response = await request(app)
        .get('/preferences')
        .set('Authorization', validJWT)
        .expect(200);

      expect(response.body).toMatchObject({
        userId: expect.any(String),
        preferences: expect.arrayContaining([
          expect.objectContaining({
            id: expect.toBeValidUUID(),
            type: expect.stringMatching(/^(welcome|order|payment|system|promotional)$/),
            channel: expect.stringMatching(/^(email|sms|in_app)$/),
            enabled: expect.any(Boolean),
            frequency: expect.stringMatching(/^(immediate|daily|weekly|disabled)$/),
            createdAt: expect.any(String),
            updatedAt: expect.any(String),
          }),
        ]),
      });
    });

    it('should return 401 for missing authorization', async() => {
      const response = await request(app)
        .get('/preferences')
        .expect(401);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
        timestamp: expect.any(String),
        path: '/preferences',
      });
    });

    it('should return empty preferences for new user', async() => {
      // This test assumes that a new user has no preferences set
      const response = await request(app)
        .get('/preferences')
        .set('Authorization', 'Bearer new-user-token')
        .expect(200);

      expect(response.body).toMatchObject({
        userId: expect.any(String),
        preferences: [],
      });
    });

    it('should return JSON content type', async() => {
      const response = await request(app)
        .get('/preferences')
        .set('Authorization', validJWT)
        .expect('Content-Type', /json/);

      expect(response.body).toBeDefined();
    });
  });

  describe('PUT /preferences', () => {
    const validPreferencesRequest = {
      preferences: [
        {
          type: 'order',
          channel: 'email',
          enabled: true,
          frequency: 'immediate',
        },
        {
          type: 'order',
          channel: 'sms',
          enabled: false,
          frequency: 'disabled',
        },
        {
          type: 'promotional',
          channel: 'email',
          enabled: false,
          frequency: 'disabled',
        },
        {
          type: 'system',
          channel: 'in_app',
          enabled: true,
          frequency: 'immediate',
        },
      ],
    };

    it('should return 200 with updated preferences', async() => {
      const response = await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send(validPreferencesRequest)
        .expect(200);

      expect(response.body).toMatchObject({
        userId: expect.any(String),
        preferences: expect.arrayContaining([
          expect.objectContaining({
            id: expect.toBeValidUUID(),
            type: 'order',
            channel: 'email',
            enabled: true,
            frequency: 'immediate',
            updatedAt: expect.any(String),
          }),
          expect.objectContaining({
            id: expect.toBeValidUUID(),
            type: 'order',
            channel: 'sms',
            enabled: false,
            frequency: 'disabled',
            updatedAt: expect.any(String),
          }),
          expect.objectContaining({
            id: expect.toBeValidUUID(),
            type: 'promotional',
            channel: 'email',
            enabled: false,
            frequency: 'disabled',
            updatedAt: expect.any(String),
          }),
          expect.objectContaining({
            id: expect.toBeValidUUID(),
            type: 'system',
            channel: 'in_app',
            enabled: true,
            frequency: 'immediate',
            updatedAt: expect.any(String),
          }),
        ]),
      });

      // Should have exactly the number of preferences we sent
      expect(response.body.preferences).toHaveLength(4);
    });

    it('should return 401 for missing authorization', async() => {
      const response = await request(app)
        .put('/preferences')
        .send(validPreferencesRequest)
        .expect(401);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
        timestamp: expect.any(String),
        path: '/preferences',
      });
    });

    it('should return 422 for missing required fields', async() => {
      const invalidRequest = {
        preferences: [
          {
            type: 'order',
            // missing channel and enabled
          },
        ],
      };

      const response = await request(app)
        .put('/preferences')
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
        path: '/preferences',
      });
    });

    it('should return 400 for invalid notification type', async() => {
      const invalidRequest = {
        preferences: [
          {
            type: 'invalid-type',
            channel: 'email',
            enabled: true,
            frequency: 'immediate',
          },
        ],
      };

      const response = await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send(invalidRequest)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('type'),
      });
    });

    it('should return 400 for invalid channel', async() => {
      const invalidRequest = {
        preferences: [
          {
            type: 'order',
            channel: 'invalid-channel',
            enabled: true,
            frequency: 'immediate',
          },
        ],
      };

      const response = await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send(invalidRequest)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('channel'),
      });
    });

    it('should return 400 for invalid frequency', async() => {
      const invalidRequest = {
        preferences: [
          {
            type: 'order',
            channel: 'email',
            enabled: true,
            frequency: 'invalid-frequency',
          },
        ],
      };

      const response = await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send(invalidRequest)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('frequency'),
      });
    });

    it('should handle duplicate type/channel combinations', async() => {
      const duplicateRequest = {
        preferences: [
          {
            type: 'order',
            channel: 'email',
            enabled: true,
            frequency: 'immediate',
          },
          {
            type: 'order',
            channel: 'email', // Duplicate type/channel
            enabled: false,
            frequency: 'disabled',
          },
        ],
      };

      const response = await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send(duplicateRequest)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('duplicate'),
      });
    });

    it('should allow partial preference updates', async() => {
      const partialRequest = {
        preferences: [
          {
            type: 'promotional',
            channel: 'email',
            enabled: false,
            frequency: 'disabled',
          },
        ],
      };

      const response = await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send(partialRequest)
        .expect(200);

      expect(response.body).toMatchObject({
        userId: expect.any(String),
        preferences: expect.arrayContaining([
          expect.objectContaining({
            type: 'promotional',
            channel: 'email',
            enabled: false,
            frequency: 'disabled',
          }),
        ]),
      });

      // Should have at least the preference we set
      expect(response.body.preferences.length).toBeGreaterThanOrEqual(1);
    });

    it('should maintain existing preferences not in update', async() => {
      // First, set some preferences
      const initialRequest = {
        preferences: [
          {
            type: 'order',
            channel: 'email',
            enabled: true,
            frequency: 'immediate',
          },
          {
            type: 'system',
            channel: 'in_app',
            enabled: true,
            frequency: 'immediate',
          },
        ],
      };

      await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send(initialRequest)
        .expect(200);

      // Then update only one preference
      const updateRequest = {
        preferences: [
          {
            type: 'order',
            channel: 'email',
            enabled: false,
            frequency: 'disabled',
          },
        ],
      };

      const response = await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send(updateRequest)
        .expect(200);

      // Should still have both preferences, but order/email should be updated
      const orderEmailPref = response.body.preferences.find(
        p => p.type === 'order' && p.channel === 'email'
      );
      const systemInAppPref = response.body.preferences.find(
        p => p.type === 'system' && p.channel === 'in_app'
      );

      expect(orderEmailPref).toMatchObject({
        enabled: false,
        frequency: 'disabled',
      });

      expect(systemInAppPref).toMatchObject({
        enabled: true,
        frequency: 'immediate',
      });
    });
  });
});