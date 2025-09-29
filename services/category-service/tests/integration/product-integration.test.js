const request = require('supertest');
const { Category } = require('../../src/models');
const { sequelize } = require('../../src/models');

describe('Product Catalog Integration Tests', () => {
  let app;
  let authToken;

  beforeAll(async () => {
    try {
      app = require('../../src/app');
      authToken = 'mock-admin-token';

      // Ensure database is synced
      await sequelize.sync({ force: true });
    } catch (error) {
      console.error('Setup error:', error);
      app = null;
    }
  });

  beforeEach(async () => {
    if (app) {
      // Clean up categories before each test
      await Category.destroy({ where: {}, force: true });
    }
  });

  afterAll(async () => {
    if (sequelize) {
      await sequelize.close();
    }
  });

  test('should retrieve products for a category', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create test category
    const categoryResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Electronics',
        description: 'Electronic products category'
      });

    expect(categoryResponse.status).toBe(201);
    const categoryId = categoryResponse.body.id;

    // Get products for the category
    const productsResponse = await request(app)
      .get(`/categories/${categoryId}/products`);

    expect(productsResponse.status).toBe(200);
    expect(productsResponse.body).toHaveProperty('products');
    expect(productsResponse.body).toHaveProperty('pagination');
    expect(productsResponse.body).toHaveProperty('category');

    expect(productsResponse.body.category.id).toBe(categoryId);
    expect(productsResponse.body.category.name).toBe('Electronics');
  });

  test('should handle product catalog service unavailability', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create test category
    const categoryResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Electronics',
        description: 'Electronic products category'
      });

    const categoryId = categoryResponse.body.id;

    // Mock scenario where product catalog service is unavailable
    const productsResponse = await request(app)
      .get(`/categories/${categoryId}/products`)
      .set('X-Mock-Service-Unavailable', 'product-catalog');

    // Should handle gracefully with appropriate error response
    expect([200, 503]).toContain(productsResponse.status);

    if (productsResponse.status === 503) {
      expect(productsResponse.body.error.code).toBe('SERVICE_UNAVAILABLE');
      expect(productsResponse.body.error.message).toContain('product catalog');
    } else {
      // If graceful degradation, should return empty products or cached data
      expect(productsResponse.body.products).toBeDefined();
    }
  });

  test('should support pagination in product retrieval', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create test category
    const categoryResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Electronics',
        description: 'Electronic products category'
      });

    const categoryId = categoryResponse.body.id;

    // Get products with pagination parameters
    const productsResponse = await request(app)
      .get(`/categories/${categoryId}/products`)
      .query({
        page: 1,
        limit: 10
      });

    expect(productsResponse.status).toBe(200);
    expect(productsResponse.body.pagination).toMatchObject({
      page: 1,
      limit: 10
    });
    expect(productsResponse.body.pagination).toHaveProperty('total');
    expect(productsResponse.body.pagination).toHaveProperty('pages');
    expect(productsResponse.body.pagination).toHaveProperty('has_next');
    expect(productsResponse.body.pagination).toHaveProperty('has_prev');
  });

  test('should include subcategory products when requested', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create parent and child categories
    const parentResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Electronics',
        description: 'Electronic products category'
      });

    const childResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Smartphones',
        description: 'Mobile phones',
        parent_id: parentResponse.body.id
      });

    const parentId = parentResponse.body.id;

    // Get products including subcategories
    const productsResponse = await request(app)
      .get(`/categories/${parentId}/products`)
      .query({
        include_subcategories: true
      });

    expect(productsResponse.status).toBe(200);
    expect(productsResponse.body.filters.include_subcategories).toBe(true);

    // Should include products from both parent and child categories
    expect(productsResponse.body.products).toBeDefined();
  });

  test('should provide product count for categories', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create test category
    const categoryResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Electronics',
        description: 'Electronic products category'
      });

    const categoryId = categoryResponse.body.id;

    // Get categories with product count
    const categoriesResponse = await request(app)
      .get('/categories')
      .query({
        include_product_count: true
      });

    expect(categoriesResponse.status).toBe(200);
    expect(categoriesResponse.body.categories).toHaveLength(1);
    expect(categoriesResponse.body.categories[0]).toHaveProperty('product_count');
    expect(typeof categoriesResponse.body.categories[0].product_count).toBe('number');
  });

  test('should handle invalid category ID for product retrieval', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    const invalidCategoryId = 999999;

    const productsResponse = await request(app)
      .get(`/categories/${invalidCategoryId}/products`);

    expect(productsResponse.status).toBe(404);
    expect(productsResponse.body.error.code).toBe('CATEGORY_NOT_FOUND');
  });

  test('should handle timeout from product catalog service', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create test category
    const categoryResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Electronics',
        description: 'Electronic products category'
      });

    const categoryId = categoryResponse.body.id;

    // Mock timeout scenario
    const productsResponse = await request(app)
      .get(`/categories/${categoryId}/products`)
      .set('X-Mock-Service-Timeout', 'product-catalog');

    // Should handle timeout gracefully
    expect([200, 503, 504]).toContain(productsResponse.status);

    if (productsResponse.status === 504) {
      expect(productsResponse.body.error.code).toBe('GATEWAY_TIMEOUT');
    } else if (productsResponse.status === 503) {
      expect(productsResponse.body.error.code).toBe('SERVICE_UNAVAILABLE');
    }
  });

  test('should validate product service integration during category operations', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create category - should trigger product service notification
    const categoryResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'New Category',
        description: 'Should notify product service'
      });

    expect(categoryResponse.status).toBe(201);
    const categoryId = categoryResponse.body.id;

    // Update category - should also notify product service
    const updateResponse = await request(app)
      .put(`/categories/${categoryId}`)
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Updated Category'
      });

    expect(updateResponse.status).toBe(200);

    // Delete category - should clean up product associations
    const deleteResponse = await request(app)
      .delete(`/categories/${categoryId}`)
      .set('Authorization', `Bearer ${authToken}`);

    expect(deleteResponse.status).toBe(204);
  });

  test('should cache product counts for performance', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create test category
    const categoryResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Electronics',
        description: 'Electronic products category'
      });

    // First request - should fetch from product service
    const firstRequest = await request(app)
      .get('/categories')
      .query({ include_product_count: true });

    expect(firstRequest.status).toBe(200);

    // Second request - should use cached data (faster response)
    const secondRequest = await request(app)
      .get('/categories')
      .query({ include_product_count: true });

    expect(secondRequest.status).toBe(200);

    // Both requests should return same data
    expect(firstRequest.body.categories[0].product_count)
      .toBe(secondRequest.body.categories[0].product_count);
  });
});