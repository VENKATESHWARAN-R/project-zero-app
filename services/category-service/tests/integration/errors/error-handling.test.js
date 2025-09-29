const request = require('supertest');
const app = require('../../../src/app');
const { Category } = require('../../../src/models');

describe('Error Handling Integration', () => {
  let server;

  beforeAll(() => {
    server = app.listen(0); // Use random port for testing
  });

  afterAll(async () => {
    await server.close();
  });

  beforeEach(async () => {
    // Clean up database before each test
    await Category.destroy({ where: {}, force: true });
  });

  describe('Validation Errors', () => {
    it('should return 400 for missing required fields', async () => {
      const response = await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer valid-admin-token')
        .send({
          // Missing required 'name' field
          description: 'Test description'
        });

      expect(response.status).toBe(400);
      expect(response.body.error).toBeDefined();
      expect(response.body.error.code).toBe('VALIDATION_ERROR');
      expect(response.body.error.message).toContain('name');
      expect(response.body.timestamp).toBeDefined();
      expect(response.body.request_id).toBeDefined();
    });

    it('should return 400 for invalid field types', async () => {
      const response = await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer valid-admin-token')
        .send({
          name: 123, // Should be string
          parent_id: 'invalid' // Should be number
        });

      expect(response.status).toBe(400);
      expect(response.body.error.code).toBe('VALIDATION_ERROR');
      expect(response.body.error.details).toBeDefined();
    });

    it('should return 400 for field length violations', async () => {
      const response = await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer valid-admin-token')
        .send({
          name: 'A'.repeat(101), // Exceeds 100 char limit
          description: 'Valid description'
        });

      expect(response.status).toBe(400);
      expect(response.body.error.code).toBe('VALIDATION_ERROR');
      expect(response.body.error.details.field).toBe('name');
    });

    it('should return 400 for invalid URL format', async () => {
      const response = await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer valid-admin-token')
        .send({
          name: 'Test Category',
          image_url: 'not-a-valid-url'
        });

      expect(response.status).toBe(400);
      expect(response.body.error.code).toBe('VALIDATION_ERROR');
      expect(response.body.error.details.field).toBe('image_url');
    });
  });

  describe('Authentication Errors', () => {
    it('should return 401 for missing authorization header', async () => {
      const response = await request(app)
        .post('/categories')
        .send({
          name: 'Test Category'
        });

      expect(response.status).toBe(401);
      expect(response.body.error.code).toBe('UNAUTHORIZED');
      expect(response.body.error.message).toContain('authentication');
    });

    it('should return 401 for invalid token format', async () => {
      const response = await request(app)
        .post('/categories')
        .set('Authorization', 'InvalidTokenFormat')
        .send({
          name: 'Test Category'
        });

      expect(response.status).toBe(401);
      expect(response.body.error.code).toBe('INVALID_TOKEN');
    });

    it('should return 401 for expired token', async () => {
      const response = await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer expired-token')
        .send({
          name: 'Test Category'
        });

      expect(response.status).toBe(401);
      expect(response.body.error.code).toBe('TOKEN_EXPIRED');
    });
  });

  describe('Authorization Errors', () => {
    it('should return 403 for non-admin user', async () => {
      const response = await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer valid-user-token') // Not admin
        .send({
          name: 'Test Category'
        });

      expect(response.status).toBe(403);
      expect(response.body.error.code).toBe('INSUFFICIENT_PERMISSIONS');
      expect(response.body.error.message).toContain('admin');
    });
  });

  describe('Resource Not Found Errors', () => {
    it('should return 404 for non-existent category', async () => {
      const response = await request(app)
        .get('/categories/999');

      expect(response.status).toBe(404);
      expect(response.body.error.code).toBe('CATEGORY_NOT_FOUND');
      expect(response.body.error.message).toContain('Category not found');
    });

    it('should return 404 for non-existent parent category', async () => {
      const response = await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer valid-admin-token')
        .send({
          name: 'Test Category',
          parent_id: 999 // Non-existent parent
        });

      expect(response.status).toBe(404);
      expect(response.body.error.code).toBe('PARENT_CATEGORY_NOT_FOUND');
    });
  });

  describe('Business Logic Errors', () => {
    it('should return 409 for duplicate category name within same parent', async () => {
      // Create first category
      await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer valid-admin-token')
        .send({
          name: 'Electronics',
          parent_id: null
        });

      // Try to create duplicate
      const response = await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer valid-admin-token')
        .send({
          name: 'Electronics', // Same name, same parent (null)
          parent_id: null
        });

      expect(response.status).toBe(409);
      expect(response.body.error.code).toBe('CATEGORY_NAME_CONFLICT');
    });

    it('should return 409 for circular hierarchy', async () => {
      // Create parent category
      const parentResponse = await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer valid-admin-token')
        .send({
          name: 'Parent Category'
        });

      const parentId = parentResponse.body.id;

      // Try to make parent a child of itself
      const response = await request(app)
        .put(`/categories/${parentId}`)
        .set('Authorization', 'Bearer valid-admin-token')
        .send({
          parent_id: parentId
        });

      expect(response.status).toBe(409);
      expect(response.body.error.code).toBe('CIRCULAR_HIERARCHY');
    });

    it('should return 400 for exceeding maximum hierarchy depth', async () => {
      let currentParentId = null;

      // Create 5 levels of hierarchy (maximum allowed)
      for (let i = 1; i <= 5; i++) {
        const response = await request(app)
          .post('/categories')
          .set('Authorization', 'Bearer valid-admin-token')
          .send({
            name: `Level ${i}`,
            parent_id: currentParentId
          });

        currentParentId = response.body.id;
      }

      // Try to create 6th level (should fail)
      const response = await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer valid-admin-token')
        .send({
          name: 'Level 6',
          parent_id: currentParentId
        });

      expect(response.status).toBe(400);
      expect(response.body.error.code).toBe('MAX_HIERARCHY_DEPTH_EXCEEDED');
    });

    it('should return 400 when trying to delete category with active children', async () => {
      // Create parent category
      const parentResponse = await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer valid-admin-token')
        .send({
          name: 'Parent Category'
        });

      const parentId = parentResponse.body.id;

      // Create child category
      await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer valid-admin-token')
        .send({
          name: 'Child Category',
          parent_id: parentId
        });

      // Try to delete parent (should fail)
      const response = await request(app)
        .delete(`/categories/${parentId}`)
        .set('Authorization', 'Bearer valid-admin-token');

      expect(response.status).toBe(400);
      expect(response.body.error.code).toBe('CATEGORY_HAS_CHILDREN');
    });
  });

  describe('Rate Limiting Errors', () => {
    it('should return 429 when rate limit exceeded', async () => {
      const requests = [];

      // Send many requests rapidly
      for (let i = 0; i < 150; i++) { // Exceeds limit of 100 per 15 minutes
        requests.push(
          request(app)
            .get('/categories')
            .set('X-Forwarded-For', '127.0.0.1') // Same IP
        );
      }

      const responses = await Promise.all(requests);

      // Should have some 429 responses
      const rateLimitedResponses = responses.filter(r => r.status === 429);
      expect(rateLimitedResponses.length).toBeGreaterThan(0);

      if (rateLimitedResponses.length > 0) {
        expect(rateLimitedResponses[0].body.error.code).toBe('RATE_LIMIT_EXCEEDED');
        expect(rateLimitedResponses[0].headers['retry-after']).toBeDefined();
      }
    }, 10000); // Increase timeout for this test
  });

  describe('External Service Errors', () => {
    it('should return 503 when auth service is unavailable', async () => {
      // Mock auth service failure
      jest.spyOn(require('../../../src/integrations/authService'), 'verifyToken')
        .mockRejectedValue(new Error('Service unavailable'));

      const response = await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer valid-admin-token')
        .send({
          name: 'Test Category'
        });

      expect(response.status).toBe(503);
      expect(response.body.error.code).toBe('SERVICE_UNAVAILABLE');
      expect(response.body.error.details.service).toBe('auth-service');
    });

    it('should return 503 when product service is unavailable', async () => {
      const response = await request(app)
        .get('/categories/1/products');

      expect(response.status).toBe(503);
      expect(response.body.error.code).toBe('SERVICE_UNAVAILABLE');
      expect(response.body.error.details.service).toBe('product-catalog');
    });
  });

  describe('Database Errors', () => {
    it('should return 500 for database connection errors', async () => {
      // Mock database failure
      jest.spyOn(Category, 'findAll')
        .mockRejectedValue(new Error('Database connection failed'));

      const response = await request(app)
        .get('/categories');

      expect(response.status).toBe(500);
      expect(response.body.error.code).toBe('INTERNAL_SERVER_ERROR');
      expect(response.body.error.message).not.toContain('Database connection failed'); // Should not leak internal details
    });
  });

  describe('Error Response Format', () => {
    it('should return consistent error format', async () => {
      const response = await request(app)
        .get('/categories/999');

      expect(response.body).toHaveProperty('error');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('request_id');

      expect(response.body.error).toHaveProperty('code');
      expect(response.body.error).toHaveProperty('message');

      expect(typeof response.body.error.code).toBe('string');
      expect(typeof response.body.error.message).toBe('string');
      expect(typeof response.body.timestamp).toBe('string');
      expect(typeof response.body.request_id).toBe('string');
    });

    it('should not leak sensitive information in error messages', async () => {
      const response = await request(app)
        .post('/categories')
        .set('Authorization', 'Bearer invalid-token')
        .send({
          name: 'Test Category'
        });

      expect(response.status).toBe(401);
      expect(response.body.error.message).not.toContain('database');
      expect(response.body.error.message).not.toContain('secret');
      expect(response.body.error.message).not.toContain('password');
      expect(response.body.error.message).not.toContain('private');
    });
  });
});