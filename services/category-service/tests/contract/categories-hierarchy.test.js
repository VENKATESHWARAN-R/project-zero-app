const request = require('supertest');

describe('GET /categories/{id}/hierarchy - Category Hierarchy Contract', () => {
  let app;

  beforeAll(async () => {
    try {
      app = require('../../src/app');
    } catch (error) {
      app = null;
    }
  });

  test('should return 200 with hierarchy information', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/1/hierarchy');

    expect(response.status).toBe(200);
    expect(response.body).toMatchObject({
      category: expect.objectContaining({
        id: 1,
        name: expect.any(String),
      }),
      ancestors: expect.any(Array),
      descendants: expect.any(Array),
      depth: expect.any(Number),
      max_depth: 5,
    });
  });

  test('should return 404 for non-existent category', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/99999/hierarchy');

    expect(response.status).toBe(404);
  });

  test('should validate depth constraints', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/1/hierarchy');

    expect(response.status).toBe(200);
    expect(response.body.depth).toBeGreaterThanOrEqual(0);
    expect(response.body.depth).toBeLessThan(5);
  });
});