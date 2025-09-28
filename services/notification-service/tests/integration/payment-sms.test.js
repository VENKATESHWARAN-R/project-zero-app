const request = require('supertest');
const app = require('../../src/app');
const { syncDatabase } = require('../../src/config/database');

describe('Payment SMS Confirmation Integration Test', () => {
  let validJWT;
  const testUserId = 'payment-user123';

  beforeAll(async() => {
    await syncDatabase({ force: true });
    validJWT = 'Bearer test-jwt-token';
  });

  describe('Payment SMS Confirmation Flow', () => {
    it('should send payment confirmation via SMS', async() => {
      const paymentSMSRequest = {
        userId: testUserId,
        templateName: 'payment_sms_confirmation',
        variables: {
          amount: '$149.99',
          orderNumber: 'ORD-2025-001',
          last4: '4242',
          merchantName: 'Project Zero Store',
        },
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(paymentSMSRequest)
        .expect(201);

      expect(response.body).toMatchObject({
        id: expect.toBeValidUUID(),
        userId: testUserId,
        channel: 'sms',
        templateId: expect.toBeValidUUID(),
        content: expect.stringContaining('$149.99'),
        content: expect.stringContaining('ORD-2025-001'),
        content: expect.stringContaining('4242'),
        status: expect.stringMatching(/^(pending|sent|delivered)$/),
      });

      // SMS content should be concise
      expect(response.body.content.length).toBeLessThan(160);
    });

    it('should handle payment confirmation with different card types', async() => {
      const cardTypes = [
        { last4: '1234', type: 'Visa' },
        { last4: '5678', type: 'Mastercard' },
        { last4: '9012', type: 'Amex' },
      ];

      for (const card of cardTypes) {
        const paymentRequest = {
          userId: testUserId,
          templateName: 'payment_sms_confirmation',
          variables: {
            amount: '$99.99',
            orderNumber: `ORD-${card.type}-001`,
            last4: card.last4,
            cardType: card.type,
          },
        };

        const response = await request(app)
          .post('/notifications/template')
          .set('Authorization', validJWT)
          .send(paymentRequest)
          .expect(201);

        expect(response.body.content).toContain(card.last4);
        expect(response.body.content).toContain(`ORD-${card.type}-001`);
      }
    });

    it('should validate SMS recipient phone number format', async() => {
      const paymentRequest = {
        userId: testUserId,
        templateName: 'payment_sms_confirmation',
        variables: {
          amount: '$75.00',
          orderNumber: 'ORD-2025-002',
          last4: '7890',
        },
        recipient: '+1-555-123-4567',
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(paymentRequest)
        .expect(201);

      expect(response.body.recipient).toBe('+1-555-123-4567');
      expect(response.body.channel).toBe('sms');
    });

    it('should reject invalid phone number formats', async() => {
      const invalidPhoneRequest = {
        userId: testUserId,
        templateName: 'payment_sms_confirmation',
        variables: {
          amount: '$50.00',
          orderNumber: 'ORD-2025-003',
          last4: '1111',
        },
        recipient: 'invalid-phone',
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(invalidPhoneRequest)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('phone'),
      });
    });

    it('should track SMS delivery status', async() => {
      const paymentRequest = {
        userId: testUserId,
        templateName: 'payment_sms_confirmation',
        variables: {
          amount: '$25.99',
          orderNumber: 'ORD-SMS-TRACK',
          last4: '3333',
        },
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(paymentRequest)
        .expect(201);

      const notificationId = response.body.id;

      // Wait for mock SMS delivery
      await new Promise(resolve => setTimeout(resolve, 800));

      const statusResponse = await request(app)
        .get(`/notifications/${notificationId}`)
        .set('Authorization', validJWT)
        .expect(200);

      expect(statusResponse.body.status).toMatch(/^(sent|delivered|failed)$/);
    });

    it('should handle concurrent payment SMS notifications', async() => {
      const paymentRequests = Array.from({ length: 5 }, (_, i) => ({
        userId: `concurrent-payment-${i}`,
        templateName: 'payment_sms_confirmation',
        variables: {
          amount: `$${(i + 1) * 20}.00`,
          orderNumber: `ORD-CONCURRENT-${i}`,
          last4: `${i}${i}${i}${i}`,
        },
      }));

      const promises = paymentRequests.map(req =>
        request(app)
          .post('/notifications/template')
          .set('Authorization', validJWT)
          .send(req)
      );

      const responses = await Promise.all(promises);

      responses.forEach((response, index) => {
        expect(response.status).toBe(201);
        expect(response.body.channel).toBe('sms');
        expect(response.body.content).toContain(`ORD-CONCURRENT-${index}`);
      });
    });
  });
});