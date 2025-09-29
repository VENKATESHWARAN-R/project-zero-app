const request = require('supertest');

describe('PUT /categories/{id} - Update Category Contract', () => {
  let app;
  const validAdminToken = 'valid-admin-jwt-token';

  beforeAll(async () => {
    try {
      app = require('../../src/app');
    } catch (error) {
      app = null;
    }
  });

  test('should return 200 when updating category with valid data', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const updateData = {
      name: 'Updated Electronics',
      description: 'Updated description',
    };

    const response = await request(app)
      .put('/categories/1')
      .set('Authorization', `Bearer ${validAdminToken}`)
      .send(updateData);

    expect(response.status).toBe(200);
    expect(response.body).toMatchObject({
      id: 1,
      name: updateData.name,
      description: updateData.description,
      updated_at: expect.any(String),
    });
  });

  test('should return 401 without authentication', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app)
      .put('/categories/1')
      .send({ name: 'Updated' });

    expect(response.status).toBe(401);
  });

  test('should return 404 for non-existent category', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app)
      .put('/categories/99999')
      .set('Authorization', `Bearer ${validAdminToken}`)
      .send({ name: 'Updated' });

    expect(response.status).toBe(404);
  });

  test('should return 400 for circular hierarchy', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app)
      .put('/categories/1')
      .set('Authorization', `Bearer ${validAdminToken}`)
      .send({ parent_id: 1 }); // Self-reference

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('CIRCULAR_HIERARCHY');
  });
});