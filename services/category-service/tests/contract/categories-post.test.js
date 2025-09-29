const request = require('supertest');

describe('POST /categories - Create Category Contract', () => {
  let app;
  const validAdminToken = 'valid-admin-jwt-token';
  const invalidToken = 'invalid-jwt-token';

  beforeAll(async () => {
    try {
      app = require('../../src/app');
    } catch (error) {
      app = null;
    }
  });

  test('should return 201 when creating valid category with admin token', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const categoryData = {
      name: 'Electronics',
      description: 'Electronic devices and accessories',
      image_url: 'https://example.com/electronics.jpg',
    };

    const response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${validAdminToken}`)
      .send(categoryData);

    expect(response.status).toBe(201);
    expect(response.body).toMatchObject({
      id: expect.any(Number),
      name: categoryData.name,
      slug: expect.any(String),
      description: categoryData.description,
      image_url: categoryData.image_url,
      parent_id: null,
      sort_order: expect.any(Number),
      is_active: true,
      created_at: expect.any(String),
      updated_at: expect.any(String),
    });
  });

  test('should return 401 without authentication token', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const categoryData = {
      name: 'Electronics',
    };

    const response = await request(app).post('/categories').send(categoryData);

    expect(response.status).toBe(401);
    expect(response.body).toHaveProperty('error');
  });

  test('should return 401 with invalid token', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const categoryData = {
      name: 'Electronics',
    };

    const response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${invalidToken}`)
      .send(categoryData);

    expect(response.status).toBe(401);
    expect(response.body).toHaveProperty('error');
  });

  test('should return 400 for missing required name field', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const categoryData = {
      description: 'Missing name field',
    };

    const response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${validAdminToken}`)
      .send(categoryData);

    expect(response.status).toBe(400);
    expect(response.body).toHaveProperty('error');
  });

  test('should return 400 for invalid name length', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const categoryData = {
      name: 'a'.repeat(101), // Exceeds 100 character limit
    };

    const response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${validAdminToken}`)
      .send(categoryData);

    expect(response.status).toBe(400);
    expect(response.body).toHaveProperty('error');
  });

  test('should return 400 for invalid image_url format', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const categoryData = {
      name: 'Electronics',
      image_url: 'not-a-valid-url',
    };

    const response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${validAdminToken}`)
      .send(categoryData);

    expect(response.status).toBe(400);
    expect(response.body).toHaveProperty('error');
  });

  test('should auto-generate slug from name', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const categoryData = {
      name: 'Gaming Laptops',
    };

    const response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${validAdminToken}`)
      .send(categoryData);

    expect(response.status).toBe(201);
    expect(response.body.slug).toBe('gaming-laptops');
  });
});