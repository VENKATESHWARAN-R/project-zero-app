const request = require('supertest');

describe('GET /categories/search - Search Categories Contract', () => {
  let app;

  beforeAll(async () => {
    try {
      app = require('../../src/app');
    } catch (error) {
      app = null;
    }
  });

  test('should return 200 with search results', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/search?q=electronics');

    expect(response.status).toBe(200);
    expect(response.body).toMatchObject({
      categories: expect.any(Array),
      query: 'electronics',
      total: expect.any(Number),
    });
  });

  test('should return 400 for missing search query', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/search');

    expect(response.status).toBe(400);
    expect(response.body).toHaveProperty('error');
  });

  test('should support active_only parameter', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/search?q=test&active_only=false');

    expect(response.status).toBe(200);
  });
});