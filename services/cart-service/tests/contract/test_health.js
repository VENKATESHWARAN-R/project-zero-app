const request = require('supertest');

// Contract Test: GET /health
// Tests API specification compliance for health endpoint
// Expected: 200 status with health object containing status, timestamp, database fields

describe('Contract Test: GET /health', () => {
  let app;

  beforeAll(() => {
    try {
      app = require('../../src/app');
    } catch (error) {
      // App not yet implemented
      app = null;
    }
  });

  test('should return 200 with valid health response structure', async () => {
    if (!app) {
      expect(true).toBe(false); // Force test to fail - implementation required
      return;
    }

    const response = await request(app)
      .get('/health')
      .expect('Content-Type', /json/)
      .expect(200);

    // Validate response structure according to API spec
    expect(response.body).toHaveProperty('status');
    expect(response.body).toHaveProperty('timestamp');
    expect(response.body).toHaveProperty('database');

    // Validate data types
    expect(typeof response.body.status).toBe('string');
    expect(typeof response.body.timestamp).toBe('string');
    expect(typeof response.body.database).toBe('string');

    // Validate expected values
    expect(response.body.status).toBe('healthy');
    expect(response.body.database).toBe('connected');

    // Validate timestamp format (ISO 8601)
    expect(response.body.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z$/);
  });

  test('should respond within acceptable time (<200ms)', async () => {
    if (!app) {
      expect(true).toBe(false); // Force test to fail - implementation required
      return;
    }

    const startTime = Date.now();
    await request(app).get('/health').expect(200);
    const responseTime = Date.now() - startTime;

    expect(responseTime).toBeLessThan(200);
  });
});