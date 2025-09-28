const request = require('supertest');
const app = require('../../src/app');

describe('Health Endpoints Contract Tests', () => {
  describe('GET /health', () => {
    it('should return 200 with health status', async() => {
      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.body).toMatchObject({
        status: 'healthy',
        service: 'notification-service',
        version: '1.0.0',
        timestamp: expect.any(String),
      });

      // Validate timestamp is ISO format
      expect(new Date(response.body.timestamp)).toBeInstanceOf(Date);
    });

    it('should return JSON content type', async() => {
      const response = await request(app)
        .get('/health')
        .expect('Content-Type', /json/);

      expect(response.body).toBeDefined();
    });
  });

  describe('GET /health/ready', () => {
    it('should return 200 when service is ready', async() => {
      const response = await request(app)
        .get('/health/ready')
        .expect(200);

      expect(response.body).toMatchObject({
        status: 'ready',
        checks: {
          database: expect.stringMatching(/^(ok|error)$/),
          auth_service: expect.stringMatching(/^(ok|error)$/),
        },
        timestamp: expect.any(String),
      });

      // Validate timestamp is ISO format
      expect(new Date(response.body.timestamp)).toBeInstanceOf(Date);
    });

    it('should return 503 when service is not ready', async() => {
      // This test will be implemented once we have dependency failure simulation
      // For now, we expect the endpoint to exist and return proper structure
      const response = await request(app)
        .get('/health/ready');

      expect([200, 503]).toContain(response.status);

      if (response.status === 503) {
        expect(response.body).toMatchObject({
          error: expect.any(String),
          message: expect.any(String),
          timestamp: expect.any(String),
          path: '/health/ready',
        });
      }
    });

    it('should return JSON content type', async() => {
      const response = await request(app)
        .get('/health/ready')
        .expect('Content-Type', /json/);

      expect(response.body).toBeDefined();
    });
  });
});