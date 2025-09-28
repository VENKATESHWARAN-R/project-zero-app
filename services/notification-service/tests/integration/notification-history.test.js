const request = require('supertest');
const app = require('../../src/app');
const { syncDatabase } = require('../../src/config/database');

describe('Notification History Integration Test', () => {
  let validJWT;
  const testUserId = 'history-user123';

  beforeAll(async() => {
    await syncDatabase({ force: true });
    validJWT = 'Bearer test-jwt-token';
  });

  describe('Notification History Retrieval', () => {
    beforeEach(async() => {
      // Create test notifications for history
      const notifications = [
        { channel: 'email', content: 'Email notification 1' },
        { channel: 'sms', content: 'SMS notification 1' },
        { channel: 'in_app', content: 'In-app notification 1' },
        { channel: 'email', content: 'Email notification 2' },
      ];

      for (const notif of notifications) {
        await request(app)
          .post('/notifications')
          .set('Authorization', validJWT)
          .send({
            userId: testUserId,
            ...notif,
            recipient: notif.channel === 'email' ? 'test@example.com' : '+1-555-123-4567',
          });
      }
    });

    it('should retrieve paginated notification history', async() => {
      const response = await request(app)
        .get('/notifications?page=1&limit=2')
        .set('Authorization', validJWT)
        .expect(200);

      expect(response.body).toMatchObject({
        notifications: expect.any(Array),
        pagination: {
          page: 1,
          limit: 2,
          totalPages: expect.any(Number),
          totalCount: expect.any(Number),
          hasNext: expect.any(Boolean),
          hasPrevious: false,
        },
      });

      expect(response.body.notifications).toHaveLength(2);
    });

    it('should filter notifications by channel', async() => {
      const response = await request(app)
        .get('/notifications?channel=email')
        .set('Authorization', validJWT)
        .expect(200);

      response.body.notifications.forEach(notification => {
        expect(notification.channel).toBe('email');
      });
    });

    it('should filter notifications by status', async() => {
      const response = await request(app)
        .get('/notifications?status=sent')
        .set('Authorization', validJWT)
        .expect(200);

      response.body.notifications.forEach(notification => {
        expect(notification.status).toBe('sent');
      });
    });

    it('should filter notifications by date range', async() => {
      const startDate = new Date(Date.now() - 86400000).toISOString(); // 24 hours ago
      const endDate = new Date().toISOString();

      const response = await request(app)
        .get(`/notifications?startDate=${startDate}&endDate=${endDate}`)
        .set('Authorization', validJWT)
        .expect(200);

      response.body.notifications.forEach(notification => {
        const createdAt = new Date(notification.createdAt);
        expect(createdAt).toBeInstanceOf(Date);
        expect(createdAt.getTime()).toBeGreaterThanOrEqual(new Date(startDate).getTime());
        expect(createdAt.getTime()).toBeLessThanOrEqual(new Date(endDate).getTime());
      });
    });

    it('should return only user-specific notifications', async() => {
      const response = await request(app)
        .get('/notifications')
        .set('Authorization', validJWT)
        .expect(200);

      response.body.notifications.forEach(notification => {
        expect(notification.userId).toBe(testUserId);
      });
    });
  });
});