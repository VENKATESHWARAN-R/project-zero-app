const request = require('supertest');
const app = require('../../src/app');
const { syncDatabase } = require('../../src/config/database');

describe('User Preferences Integration Test', () => {
  let validJWT;
  const testUserId = 'preferences-user123';

  beforeAll(async() => {
    await syncDatabase({ force: true });
    validJWT = 'Bearer test-jwt-token';
  });

  describe('User Preference Management', () => {
    it('should create and retrieve user preferences', async() => {
      const preferencesRequest = {
        preferences: [
          {
            type: 'order',
            channel: 'email',
            enabled: true,
            frequency: 'immediate',
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

      const updateResponse = await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send(preferencesRequest)
        .expect(200);

      expect(updateResponse.body).toMatchObject({
        userId: testUserId,
        preferences: expect.arrayContaining([
          expect.objectContaining({
            type: 'order',
            channel: 'email',
            enabled: true,
            frequency: 'immediate',
          }),
          expect.objectContaining({
            type: 'promotional',
            channel: 'email',
            enabled: false,
            frequency: 'disabled',
          }),
          expect.objectContaining({
            type: 'system',
            channel: 'in_app',
            enabled: true,
            frequency: 'immediate',
          }),
        ]),
      });

      // Retrieve preferences
      const getResponse = await request(app)
        .get('/preferences')
        .set('Authorization', validJWT)
        .expect(200);

      expect(getResponse.body).toMatchObject(updateResponse.body);
    });

    it('should respect disabled preferences when sending notifications', async() => {
      // Disable promotional emails
      await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send({
          preferences: [
            {
              type: 'promotional',
              channel: 'email',
              enabled: false,
              frequency: 'disabled',
            },
          ],
        })
        .expect(200);

      // Try to send promotional notification
      const response = await request(app)
        .post('/notifications')
        .set('Authorization', validJWT)
        .send({
          userId: testUserId,
          channel: 'email',
          recipient: 'test@example.com',
          content: 'Promotional content',
          metadata: { type: 'promotional' },
        })
        .expect(400);

      expect(response.body.message).toContain('disabled');
    });

    it('should allow system notifications even when disabled', async() => {
      // Try to disable system notifications
      await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send({
          preferences: [
            {
              type: 'system',
              channel: 'in_app',
              enabled: false,
              frequency: 'disabled',
            },
          ],
        })
        .expect(200);

      // System notifications should still be allowed (in-app minimum)
      const response = await request(app)
        .post('/notifications')
        .set('Authorization', validJWT)
        .send({
          userId: testUserId,
          channel: 'in_app',
          recipient: testUserId,
          content: 'System maintenance notification',
          metadata: { type: 'system' },
        })
        .expect(201);

      expect(response.body.channel).toBe('in_app');
    });

    it('should update preferences incrementally', async() => {
      // Set initial preferences
      await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send({
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
              enabled: true,
              frequency: 'immediate',
            },
          ],
        })
        .expect(200);

      // Update only one preference
      const updateResponse = await request(app)
        .put('/preferences')
        .set('Authorization', validJWT)
        .send({
          preferences: [
            {
              type: 'order',
              channel: 'email',
              enabled: false,
              frequency: 'disabled',
            },
          ],
        })
        .expect(200);

      // Check that SMS preference is maintained
      const orderSMSPref = updateResponse.body.preferences.find(
        p => p.type === 'order' && p.channel === 'sms'
      );
      expect(orderSMSPref).toMatchObject({
        enabled: true,
        frequency: 'immediate',
      });

      // Check that email preference is updated
      const orderEmailPref = updateResponse.body.preferences.find(
        p => p.type === 'order' && p.channel === 'email'
      );
      expect(orderEmailPref).toMatchObject({
        enabled: false,
        frequency: 'disabled',
      });
    });
  });
});