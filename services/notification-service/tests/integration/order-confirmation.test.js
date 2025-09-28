const request = require('supertest');
const app = require('../../src/app');
const { syncDatabase } = require('../../src/config/database');

describe('Order Confirmation Integration Test', () => {
  let validJWT;
  const testUserId = 'customer123';

  beforeAll(async() => {
    await syncDatabase({ force: true });
    validJWT = 'Bearer test-jwt-token';
  });

  describe('Order Confirmation Flow', () => {
    it('should send order confirmation notification with order details', async() => {
      const orderConfirmationRequest = {
        userId: testUserId,
        templateName: 'order_email_confirmation',
        variables: {
          orderNumber: 'ORD-2025-001',
          customerName: 'John Customer',
          orderTotal: '$149.99',
          orderItems: [
            { name: 'Wireless Headphones', price: '$99.99' },
            { name: 'Phone Case', price: '$49.99' },
          ],
          estimatedDelivery: '2025-10-05',
          shippingAddress: '123 Main St, Anytown, USA',
          trackingNumber: 'TRK123456789',
        },
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(orderConfirmationRequest)
        .expect(201);

      expect(response.body).toMatchObject({
        id: expect.toBeValidUUID(),
        userId: testUserId,
        channel: 'email',
        templateId: expect.toBeValidUUID(),
        content: expect.stringContaining('ORD-2025-001'),
        content: expect.stringContaining('John Customer'),
        content: expect.stringContaining('$149.99'),
        content: expect.stringContaining('Wireless Headphones'),
        content: expect.stringContaining('2025-10-05'),
        status: expect.stringMatching(/^(pending|sent|delivered)$/),
      });

      // Verify order details are properly formatted
      expect(response.body.content).toContain('Wireless Headphones');
      expect(response.body.content).toContain('Phone Case');
      expect(response.body.content).toContain('$99.99');
      expect(response.body.content).toContain('$49.99');
    });

    it('should handle order confirmation with single item', async() => {
      const singleItemRequest = {
        userId: testUserId,
        templateName: 'order_email_confirmation',
        variables: {
          orderNumber: 'ORD-2025-002',
          customerName: 'Jane Customer',
          orderTotal: '$29.99',
          orderItems: [
            { name: 'Screen Protector', price: '$29.99' },
          ],
          estimatedDelivery: '2025-10-03',
        },
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(singleItemRequest)
        .expect(201);

      expect(response.body.content).toContain('ORD-2025-002');
      expect(response.body.content).toContain('Screen Protector');
      expect(response.body.content).toContain('$29.99');
    });

    it('should send order confirmation to custom email address', async() => {
      const customEmailRequest = {
        userId: testUserId,
        templateName: 'order_email_confirmation',
        variables: {
          orderNumber: 'ORD-2025-003',
          customerName: 'Custom Email User',
          orderTotal: '$79.99',
          orderItems: [
            { name: 'Custom Product', price: '$79.99' },
          ],
          estimatedDelivery: '2025-10-07',
        },
        recipient: 'custom.order@example.com',
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(customEmailRequest)
        .expect(201);

      expect(response.body).toMatchObject({
        recipient: 'custom.order@example.com',
        content: expect.stringContaining('ORD-2025-003'),
      });
    });

    it('should validate required order information', async() => {
      const incompleteRequest = {
        userId: testUserId,
        templateName: 'order_email_confirmation',
        variables: {
          orderNumber: 'ORD-2025-004',
          // Missing customerName, orderTotal, orderItems
        },
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(incompleteRequest)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('required'),
      });
    });

    it('should handle order confirmation with complex item structure', async() => {
      const complexOrderRequest = {
        userId: testUserId,
        templateName: 'order_email_confirmation',
        variables: {
          orderNumber: 'ORD-2025-005',
          customerName: 'Complex Order Customer',
          orderTotal: '$299.97',
          orderItems: [
            {
              name: 'Premium Wireless Headphones',
              price: '$199.99',
              quantity: 1,
              sku: 'PWH-001',
            },
            {
              name: 'Bluetooth Speaker',
              price: '$49.99',
              quantity: 2,
              sku: 'BTS-002',
            },
          ],
          estimatedDelivery: '2025-10-08',
          subtotal: '$299.97',
          tax: '$24.00',
          shipping: '$5.99',
          orderTotal: '$329.96',
        },
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(complexOrderRequest)
        .expect(201);

      expect(response.body.content).toContain('ORD-2025-005');
      expect(response.body.content).toContain('Premium Wireless Headphones');
      expect(response.body.content).toContain('Bluetooth Speaker');
      expect(response.body.content).toContain('$329.96');
    });

    it('should create notification history entry', async() => {
      const orderRequest = {
        userId: testUserId,
        templateName: 'order_email_confirmation',
        variables: {
          orderNumber: 'ORD-2025-006',
          customerName: 'History Test Customer',
          orderTotal: '$59.99',
          orderItems: [
            { name: 'Test Product', price: '$59.99' },
          ],
          estimatedDelivery: '2025-10-10',
        },
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(orderRequest)
        .expect(201);

      const notificationId = response.body.id;

      // Check notification appears in history
      const historyResponse = await request(app)
        .get('/notifications')
        .set('Authorization', validJWT)
        .expect(200);

      const notification = historyResponse.body.notifications.find(
        n => n.id === notificationId
      );

      expect(notification).toMatchObject({
        id: notificationId,
        userId: testUserId,
        content: expect.stringContaining('ORD-2025-006'),
      });
    });

    it('should support order confirmation scheduling', async() => {
      const scheduledOrderRequest = {
        userId: testUserId,
        templateName: 'order_email_confirmation',
        variables: {
          orderNumber: 'ORD-2025-007',
          customerName: 'Scheduled Customer',
          orderTotal: '$119.99',
          orderItems: [
            { name: 'Scheduled Product', price: '$119.99' },
          ],
          estimatedDelivery: '2025-10-12',
        },
        scheduledAt: '2025-09-29T10:00:00Z',
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(scheduledOrderRequest)
        .expect(201);

      expect(response.body).toMatchObject({
        userId: testUserId,
        content: expect.stringContaining('ORD-2025-007'),
        scheduledAt: '2025-09-29T10:00:00.000Z',
        status: 'pending',
      });
    });

    it('should integrate with order service for order validation', async() => {
      // This test simulates integration with order service
      // In real implementation, we would validate order exists
      const validOrderRequest = {
        userId: testUserId,
        templateName: 'order_email_confirmation',
        variables: {
          orderNumber: 'ORD-2025-008',
          customerName: 'Validated Customer',
          orderTotal: '$89.99',
          orderItems: [
            { name: 'Validated Product', price: '$89.99' },
          ],
          estimatedDelivery: '2025-10-15',
        },
        metadata: {
          orderServiceId: 'order-123',
          source: 'order-service',
        },
      };

      const response = await request(app)
        .post('/notifications/template')
        .set('Authorization', validJWT)
        .send(validOrderRequest)
        .expect(201);

      expect(response.body.metadata).toMatchObject({
        orderServiceId: 'order-123',
        source: 'order-service',
      });
    });

    it('should handle high volume order confirmations', async() => {
      const orderRequests = Array.from({ length: 10 }, (_, i) => ({
        userId: `bulk-customer-${i}`,
        templateName: 'order_email_confirmation',
        variables: {
          orderNumber: `ORD-BULK-${i.toString().padStart(3, '0')}`,
          customerName: `Bulk Customer ${i}`,
          orderTotal: `$${(i + 1) * 10}.99`,
          orderItems: [
            { name: `Bulk Product ${i}`, price: `$${(i + 1) * 10}.99` },
          ],
          estimatedDelivery: '2025-10-20',
        },
      }));

      const promises = orderRequests.map(orderReq =>
        request(app)
          .post('/notifications/template')
          .set('Authorization', validJWT)
          .send(orderReq)
      );

      const responses = await Promise.all(promises);

      // All should succeed
      responses.forEach((response, index) => {
        expect(response.status).toBe(201);
        expect(response.body.content).toContain(`ORD-BULK-${index.toString().padStart(3, '0')}`);
      });

      // Check all notifications appear in history
      const historyResponse = await request(app)
        .get('/notifications?limit=50')
        .set('Authorization', validJWT)
        .expect(200);

      const bulkNotifications = historyResponse.body.notifications.filter(
        n => n.content && n.content.includes('ORD-BULK-')
      );

      expect(bulkNotifications.length).toBeGreaterThanOrEqual(10);
    });
  });
});