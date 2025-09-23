const request = require('supertest');
const express = require('express');
const { validateAddItem, validateUpdateQuantity, validateRemoveItem } = require('../../src/middleware/validation');

// Create test app with validation middleware
const createTestApp = (validationMiddleware) => {
  const app = express();
  app.use(express.json());

  app.post('/test', validationMiddleware, (req, res) => {
    res.json({ success: true, body: req.body, params: req.params });
  });

  app.put('/test/:product_id', validationMiddleware, (req, res) => {
    res.json({ success: true, body: req.body, params: req.params });
  });

  app.delete('/test/:product_id', validationMiddleware, (req, res) => {
    res.json({ success: true, body: req.body, params: req.params });
  });

  return app;
};

describe('Validation Middleware Unit Tests', () => {
  describe('validateAddItem', () => {
    let app;

    beforeEach(() => {
      app = createTestApp(validateAddItem);
    });

    test('should pass validation for valid add item request', async () => {
      const validData = {
        product_id: 'prod-123',
        quantity: 5,
      };

      const response = await request(app)
        .post('/test')
        .send(validData)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.body).toEqual(validData);
    });

    test('should fail validation for missing product_id', async () => {
      const invalidData = {
        quantity: 5,
      };

      const response = await request(app)
        .post('/test')
        .send(invalidData)
        .expect(400);

      expect(response.body.error).toBe('Validation failed');
      expect(response.body.details).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            field: 'product_id',
            message: 'Product ID is required',
          }),
        ])
      );
    });

    test('should fail validation for missing quantity', async () => {
      const invalidData = {
        product_id: 'prod-123',
      };

      const response = await request(app)
        .post('/test')
        .send(invalidData)
        .expect(400);

      expect(response.body.error).toBe('Validation failed');
      expect(response.body.details).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            field: 'quantity',
            message: 'Quantity is required',
          }),
        ])
      );
    });

    test('should fail validation for invalid quantity range', async () => {
      const testCases = [
        { quantity: 0, description: 'zero quantity' },
        { quantity: -1, description: 'negative quantity' },
        { quantity: 11, description: 'quantity above limit' },
        { quantity: 'abc', description: 'non-numeric quantity' },
      ];

      for (const testCase of testCases) {
        const invalidData = {
          product_id: 'prod-123',
          quantity: testCase.quantity,
        };

        const response = await request(app)
          .post('/test')
          .send(invalidData)
          .expect(400);

        expect(response.body.error).toBe('Validation failed');
        expect(response.body.details).toEqual(
          expect.arrayContaining([
            expect.objectContaining({
              field: 'quantity',
            }),
          ])
        );
      }
    });

    test('should fail validation for empty product_id', async () => {
      const invalidData = {
        product_id: '',
        quantity: 5,
      };

      const response = await request(app)
        .post('/test')
        .send(invalidData)
        .expect(400);

      expect(response.body.error).toBe('Validation failed');
      expect(response.body.details).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            field: 'product_id',
            message: 'Product ID is required',
          }),
        ])
      );
    });

    test('should fail validation for product_id too long', async () => {
      const invalidData = {
        product_id: 'a'.repeat(101), // 101 characters
        quantity: 5,
      };

      const response = await request(app)
        .post('/test')
        .send(invalidData)
        .expect(400);

      expect(response.body.error).toBe('Validation failed');
      expect(response.body.details).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            field: 'product_id',
            message: 'Product ID must be between 1 and 100 characters',
          }),
        ])
      );
    });
  });

  describe('validateUpdateQuantity', () => {
    let app;

    beforeEach(() => {
      app = createTestApp(validateUpdateQuantity);
    });

    test('should pass validation for valid update quantity request', async () => {
      const validData = {
        quantity: 3,
      };

      const response = await request(app)
        .put('/test/prod-123')
        .send(validData)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.body).toEqual(validData);
      expect(response.body.params.product_id).toBe('prod-123');
    });

    test('should fail validation for missing quantity', async () => {
      const response = await request(app)
        .put('/test/prod-123')
        .send({})
        .expect(400);

      expect(response.body.error).toBe('Validation failed');
      expect(response.body.details).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            field: 'quantity',
            message: 'Quantity is required',
          }),
        ])
      );
    });

    test('should fail validation for invalid quantity', async () => {
      const invalidData = {
        quantity: 15, // Above limit
      };

      const response = await request(app)
        .put('/test/prod-123')
        .send(invalidData)
        .expect(400);

      expect(response.body.error).toBe('Validation failed');
    });
  });

  describe('validateRemoveItem', () => {
    let app;

    beforeEach(() => {
      app = createTestApp(validateRemoveItem);
    });

    test('should pass validation for valid remove item request', async () => {
      const response = await request(app)
        .delete('/test/prod-123')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.params.product_id).toBe('prod-123');
    });

    test('should pass validation for product ID with special characters', async () => {
      const productId = 'prod-abc-123_def';

      const response = await request(app)
        .delete(`/test/${productId}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.params.product_id).toBe(productId);
    });
  });

  describe('error response format', () => {
    test('should include correlation_id and timestamp in error response', async () => {
      const app = createTestApp(validateAddItem);

      const response = await request(app)
        .post('/test')
        .set('X-Correlation-ID', 'test-correlation-123')
        .send({}) // Invalid data
        .expect(400);

      expect(response.body).toHaveProperty('error');
      expect(response.body).toHaveProperty('details');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('correlation_id');
      expect(response.body.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z$/);
    });

    test('should provide detailed field-level error information', async () => {
      const app = createTestApp(validateAddItem);

      const response = await request(app)
        .post('/test')
        .send({
          product_id: '', // Empty
          quantity: 'invalid', // Non-numeric
        })
        .expect(400);

      expect(response.body.details).toHaveLength(2);
      expect(response.body.details).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            field: 'product_id',
            message: expect.any(String),
            value: '',
          }),
          expect.objectContaining({
            field: 'quantity',
            message: expect.any(String),
            value: 'invalid',
          }),
        ])
      );
    });
  });
});