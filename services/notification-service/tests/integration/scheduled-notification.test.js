const request = require('supertest');
const app = require('../../src/app');
const { syncDatabase } = require('../../src/config/database');

describe('Scheduled Notification Integration Test', () => {
  let validJWT;
  const testUserId = 'scheduled-user123';

  beforeAll(async() => {
    await syncDatabase({ force: true });
    validJWT = 'Bearer test-jwt-token';
  });

  describe('Scheduled Notification Flow', () => {
    it('should create and schedule notification for future delivery', async() => {
      const futureDate = new Date(Date.now() + 3600000); // 1 hour from now
      const scheduledRequest = {
        userId: testUserId,
        channel: 'email',
        recipient: 'scheduled@example.com',
        subject: 'Scheduled Order Update',
        content: 'Your order ORD-2025-001 has shipped and will arrive by Oct 5th.',
        scheduledAt: futureDate.toISOString(),
        metadata: {
          orderNumber: 'ORD-2025-001',
          trackingNumber: 'TRK123456',
        },
      };

      const response = await request(app)
        .post('/notifications/schedule')
        .set('Authorization', validJWT)
        .send(scheduledRequest)
        .expect(201);

      expect(response.body).toMatchObject({
        id: expect.toBeValidUUID(),
        scheduleId: expect.toBeValidUUID(),
        userId: testUserId,
        status: 'pending',
        scheduledAt: futureDate.toISOString().replace(/\.\d{3}Z$/, '.000Z'),
        attempts: 0,
        maxAttempts: 3,
      });
    });

    it('should support custom retry configuration', async() => {
      const futureDate = new Date(Date.now() + 7200000); // 2 hours from now
      const customRetryRequest = {
        userId: testUserId,
        channel: 'sms',
        recipient: '+1-555-987-6543',
        content: 'Custom retry notification',
        scheduledAt: futureDate.toISOString(),
        maxAttempts: 5,
        retryInterval: 600, // 10 minutes
      };

      const response = await request(app)
        .post('/notifications/schedule')
        .set('Authorization', validJWT)
        .send(customRetryRequest)
        .expect(201);

      expect(response.body).toMatchObject({
        maxAttempts: 5,
        scheduleId: expect.toBeValidUUID(),
      });
    });

    it('should reject scheduling in the past', async() => {
      const pastDate = new Date(Date.now() - 3600000); // 1 hour ago
      const pastRequest = {
        userId: testUserId,
        channel: 'email',
        recipient: 'past@example.com',
        content: 'This should fail',
        scheduledAt: pastDate.toISOString(),
      };

      const response = await request(app)
        .post('/notifications/schedule')
        .set('Authorization', validJWT)
        .send(pastRequest)
        .expect(400);

      expect(response.body.message).toContain('future');
    });

    it('should list scheduled notifications', async() => {
      const futureDate1 = new Date(Date.now() + 10800000); // 3 hours
      const futureDate2 = new Date(Date.now() + 14400000); // 4 hours

      // Create two scheduled notifications
      await request(app)
        .post('/notifications/schedule')
        .set('Authorization', validJWT)
        .send({
          userId: testUserId,
          channel: 'email',
          recipient: 'test1@example.com',
          content: 'Scheduled test 1',
          scheduledAt: futureDate1.toISOString(),
        })
        .expect(201);

      await request(app)
        .post('/notifications/schedule')
        .set('Authorization', validJWT)
        .send({
          userId: testUserId,
          channel: 'email',
          recipient: 'test2@example.com',
          content: 'Scheduled test 2',
          scheduledAt: futureDate2.toISOString(),
        })
        .expect(201);

      // List notifications should include scheduled ones
      const response = await request(app)
        .get('/notifications?status=pending')
        .set('Authorization', validJWT)
        .expect(200);

      const scheduledNotifications = response.body.notifications.filter(
        n => n.scheduledAt && new Date(n.scheduledAt) > new Date()
      );

      expect(scheduledNotifications.length).toBeGreaterThanOrEqual(2);
    });
  });
});