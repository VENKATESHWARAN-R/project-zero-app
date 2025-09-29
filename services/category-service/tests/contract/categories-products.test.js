const request = require('supertest');

describe('GET /categories/{id}/products - Category Products Contract', () => {
  let app;

  beforeAll(async () => {
    try {
      app = require('../../src/app');
    } catch (error) {
      app = null;
    }
  });

  test('should return 200 with products list', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/1/products');

    expect(response.status).toBe(200);
    expect(response.body).toMatchObject({
      products: expect.any(Array),
      pagination: expect.objectContaining({
        page: expect.any(Number),
        limit: expect.any(Number),
        total: expect.any(Number),
        pages: expect.any(Number),
        has_next: expect.any(Boolean),
        has_prev: expect.any(Boolean),
      }),
      category: expect.objectContaining({
        id: 1,
        name: expect.any(String),
      }),
    });
  });

  test('should return 404 for non-existent category', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/99999/products');

    expect(response.status).toBe(404);
  });

  test('should support pagination parameters', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/1/products?page=2&limit=10');

    expect(response.status).toBe(200);
    expect(response.body.pagination.page).toBe(2);
    expect(response.body.pagination.limit).toBe(10);
  });

  test('should support include_subcategories parameter', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/1/products?include_subcategories=true');

    expect(response.status).toBe(200);
    expect(response.body.filters).toMatchObject({
      include_subcategories: true,
    });
  });
});