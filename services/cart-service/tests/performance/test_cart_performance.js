const request = require('supertest');
const app = require('../../src/app');

describe('Cart Performance Tests', () => {
  const authToken = 'Bearer valid-user-token';

  beforeEach(async () => {
    // Clear cart before each test
    try {
      await request(app)
        .delete('/cart')
        .set('Authorization', authToken);
    } catch (error) {
      // Cart might be empty, ignore error
    }
  });

  test('should handle add item operation within 200ms', async () => {
    const startTime = Date.now();

    await request(app)
      .post('/cart/add')
      .set('Authorization', authToken)
      .send({
        product_id: 'prod-123',
        quantity: 1,
      })
      .expect(200);

    const responseTime = Date.now() - startTime;
    expect(responseTime).toBeLessThan(200);
  });

  test('should handle get cart operation within 200ms', async () => {
    // Add an item first
    await request(app)
      .post('/cart/add')
      .set('Authorization', authToken)
      .send({
        product_id: 'prod-123',
        quantity: 1,
      });

    const startTime = Date.now();

    await request(app)
      .get('/cart')
      .set('Authorization', authToken)
      .expect(200);

    const responseTime = Date.now() - startTime;
    expect(responseTime).toBeLessThan(200);
  });

  test('should handle update item operation within 200ms', async () => {
    // Add an item first
    await request(app)
      .post('/cart/add')
      .set('Authorization', authToken)
      .send({
        product_id: 'prod-123',
        quantity: 1,
      });

    const startTime = Date.now();

    await request(app)
      .put('/cart/items/prod-123')
      .set('Authorization', authToken)
      .send({
        quantity: 3,
      })
      .expect(200);

    const responseTime = Date.now() - startTime;
    expect(responseTime).toBeLessThan(200);
  });

  test('should handle remove item operation within 200ms', async () => {
    // Add an item first
    await request(app)
      .post('/cart/add')
      .set('Authorization', authToken)
      .send({
        product_id: 'prod-123',
        quantity: 1,
      });

    const startTime = Date.now();

    await request(app)
      .delete('/cart/items/prod-123')
      .set('Authorization', authToken)
      .expect(200);

    const responseTime = Date.now() - startTime;
    expect(responseTime).toBeLessThan(200);
  });

  test('should handle clear cart operation within 200ms', async () => {
    // Add multiple items first
    await request(app)
      .post('/cart/add')
      .set('Authorization', authToken)
      .send({
        product_id: 'prod-123',
        quantity: 1,
      });

    await request(app)
      .post('/cart/add')
      .set('Authorization', authToken)
      .send({
        product_id: 'prod-laptop-123',
        quantity: 2,
      });

    const startTime = Date.now();

    await request(app)
      .delete('/cart')
      .set('Authorization', authToken)
      .expect(200);

    const responseTime = Date.now() - startTime;
    expect(responseTime).toBeLessThan(200);
  });

  test('should handle health check within 100ms', async () => {
    const startTime = Date.now();

    await request(app)
      .get('/health')
      .expect(200);

    const responseTime = Date.now() - startTime;
    expect(responseTime).toBeLessThan(100);
  });

  test('should handle readiness check within 300ms', async () => {
    const startTime = Date.now();

    await request(app)
      .get('/health/ready');

    const responseTime = Date.now() - startTime;
    expect(responseTime).toBeLessThan(300);
  });

  test('should handle concurrent requests efficiently', async () => {
    const concurrentRequests = 10;
    const promises = [];

    const startTime = Date.now();

    // Create multiple concurrent add requests
    for (let i = 0; i < concurrentRequests; i++) {
      const promise = request(app)
        .post('/cart/add')
        .set('Authorization', `Bearer user-concurrent-${i}`)
        .send({
          product_id: `prod-concurrent-${i % 3 + 1}`,
          quantity: 1,
        });
      promises.push(promise);
    }

    const results = await Promise.all(promises);
    const totalTime = Date.now() - startTime;

    // All requests should succeed
    results.forEach(response => {
      expect(response.status).toBe(200);
    });

    // Average response time should be reasonable
    const averageTime = totalTime / concurrentRequests;
    expect(averageTime).toBeLessThan(500);
  });

  test('should handle cart with many items efficiently', async () => {
    const itemCount = 20;

    // Add many items to cart
    for (let i = 1; i <= itemCount; i++) {
      await request(app)
        .post('/cart/add')
        .set('Authorization', authToken)
        .send({
          product_id: `prod-bulk-${(i % 3) + 1}`,
          quantity: 1,
        });
    }

    // Test get cart performance with many items
    const startTime = Date.now();

    const response = await request(app)
      .get('/cart')
      .set('Authorization', authToken)
      .expect(200);

    const responseTime = Date.now() - startTime;

    expect(responseTime).toBeLessThan(300);
    expect(response.body.items.length).toBeGreaterThan(0);
    expect(response.body.totals.item_count).toBe(itemCount);
  });

  test('should maintain performance under memory pressure', async () => {
    const iterations = 50;
    const responseTimes = [];

    for (let i = 0; i < iterations; i++) {
      const startTime = Date.now();

      await request(app)
        .post('/cart/add')
        .set('Authorization', `Bearer memory-test-${i}`)
        .send({
          product_id: 'prod-123',
          quantity: 1,
        })
        .expect(200);

      const responseTime = Date.now() - startTime;
      responseTimes.push(responseTime);
    }

    // Calculate average and check for performance degradation
    const averageTime = responseTimes.reduce((sum, time) => sum + time, 0) / iterations;
    const maxTime = Math.max(...responseTimes);

    expect(averageTime).toBeLessThan(200);
    expect(maxTime).toBeLessThan(500); // No single request should be too slow
  });
});