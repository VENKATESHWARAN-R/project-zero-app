const request = require('supertest');

describe('GET /health - Health Check Contract', () => {
  let app;

  beforeAll(async () => {
    app = require('../../src/app');
  });

  test('should return 200 with health status', async () => {

    const response = await request(app).get('/health');

    expect(response.status).toBe(200);
    expect(response.body).toMatchObject({
      status: expect.any(String),
      timestamp: expect.any(String),
      version: expect.any(String),
      uptime: expect.any(Number),
    });
    expect(['healthy', 'unhealthy']).toContain(response.body.status);
  });

  test('should have valid timestamp format', async () => {

    const response = await request(app).get('/health');

    expect(response.status).toBe(200);
    const timestamp = new Date(response.body.timestamp);
    expect(timestamp).toBeInstanceOf(Date);
    expect(timestamp.getTime()).not.toBeNaN();
  });

  test('should include version information', async () => {

    const response = await request(app).get('/health');

    expect(response.status).toBe(200);
    expect(response.body.version).toBeDefined();
    expect(typeof response.body.version).toBe('string');
  });
});