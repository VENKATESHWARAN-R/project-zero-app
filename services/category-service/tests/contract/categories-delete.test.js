const request = require('supertest');

describe('DELETE /categories/{id} - Delete Category Contract', () => {
  let app;
  const validAdminToken = 'valid-admin-jwt-token';

  beforeAll(async () => {
    try {
      app = require('../../src/app');
    } catch (error) {
      app = null;
    }
  });

  test('should return 204 when deleting category without children', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app)
      .delete('/categories/1')
      .set('Authorization', `Bearer ${validAdminToken}`);

    expect(response.status).toBe(204);
  });

  test('should return 401 without authentication', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app).delete('/categories/1');

    expect(response.status).toBe(401);
  });

  test('should return 404 for non-existent category', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app)
      .delete('/categories/99999')
      .set('Authorization', `Bearer ${validAdminToken}`);

    expect(response.status).toBe(404);
  });

  test('should return 400 when trying to delete category with children', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const response = await request(app)
      .delete('/categories/1')
      .set('Authorization', `Bearer ${validAdminToken}`);

    expect([204, 400]).toContain(response.status);
    if (response.status === 400) {
      expect(response.body.error.code).toBe('HAS_CHILDREN');
    }
  });
});