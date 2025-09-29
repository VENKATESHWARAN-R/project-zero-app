const request = require('supertest');

describe('GET /categories - Categories List Contract', () => {
  let app;

  beforeAll(async () => {
    try {
      app = require('../../src/app');
    } catch (error) {
      app = null;
    }
  });

  test('should return 200 with categories list', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories');

    expect(response.status).toBe(200);
    expect(response.body).toMatchObject({
      categories: expect.any(Array),
      total: expect.any(Number),
      filters: expect.any(Object),
    });
  });

  test('should filter by parent_id when provided', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories?parent_id=1');

    expect(response.status).toBe(200);
    expect(response.body.filters).toMatchObject({
      parent_id: 1,
    });
  });

  test('should include children when include_children=true', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories?include_children=true');

    expect(response.status).toBe(200);
    expect(response.body.filters.include_children).toBe(true);
  });

  test('should include product counts when include_product_count=true', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app)
      .get('/categories?include_product_count=true');

    expect(response.status).toBe(200);
    expect(response.body.filters.include_product_count).toBe(true);
  });

  test('should validate active_only parameter', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories?active_only=false');

    expect(response.status).toBe(200);
    expect(response.body.filters.active_only).toBe(false);
  });

  test('should return 400 for invalid parent_id', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories?parent_id=invalid');

    expect(response.status).toBe(400);
    expect(response.body).toHaveProperty('error');
  });
});