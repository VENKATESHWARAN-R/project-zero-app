const request = require('supertest');

describe('GET /categories/{id} - Get Category By ID Contract', () => {
  let app;

  beforeAll(async () => {
    try {
      app = require('../../src/app');
    } catch (error) {
      app = null;
    }
  });

  test('should return 200 with category details', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/1');

    expect(response.status).toBe(200);
    expect(response.body).toMatchObject({
      id: 1,
      name: expect.any(String),
      slug: expect.any(String),
      parent_id: expect.any(Number),
      sort_order: expect.any(Number),
      is_active: expect.any(Boolean),
      created_at: expect.any(String),
      updated_at: expect.any(String),
    });
  });

  test('should return 404 for non-existent category', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/99999');

    expect(response.status).toBe(404);
    expect(response.body).toHaveProperty('error');
  });

  test('should include children when include_children=true', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/1?include_children=true');

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('children');
    expect(Array.isArray(response.body.children)).toBe(true);
  });

  test('should include ancestors when include_ancestors=true', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).get('/categories/1?include_ancestors=true');

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('ancestors');
    expect(Array.isArray(response.body.ancestors)).toBe(true);
  });
});