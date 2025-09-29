const request = require('supertest');
const { Category } = require('../../src/models');
const { sequelize } = require('../../src/models');

describe('Circular Hierarchy Prevention Integration Tests', () => {
  let app;
  let authToken;

  beforeAll(async () => {
    try {
      app = require('../../src/app');
      // Mock auth token for testing
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

  test('should prevent direct circular references', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create a category
    const categoryResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Test Category',
        description: 'Category for circular test'
      });

    expect(categoryResponse.status).toBe(201);
    const categoryId = categoryResponse.body.id;

    // Try to make the category its own parent (direct self-reference)
    const circularResponse = await request(app)
      .put(`/categories/${categoryId}`)
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        parent_id: categoryId
      });

    expect(circularResponse.status).toBe(400);
    expect(circularResponse.body.error.message).toContain('parent');
  });

  test('should prevent indirect circular references', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create A -> B -> C hierarchy
    const categoryAResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Category A',
        description: 'Root category'
      });

    const categoryBResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Category B',
        description: 'Child of A',
        parent_id: categoryAResponse.body.id
      });

    const categoryCResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Category C',
        description: 'Child of B',
        parent_id: categoryBResponse.body.id
      });

    expect(categoryAResponse.status).toBe(201);
    expect(categoryBResponse.status).toBe(201);
    expect(categoryCResponse.status).toBe(201);

    // Try to make A a child of C (A->B->C->A circular reference)
    const circularResponse = await request(app)
      .put(`/categories/${categoryAResponse.body.id}`)
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        parent_id: categoryCResponse.body.id
      });

    expect(circularResponse.status).toBe(400);
    expect(circularResponse.body.error.message).toContain('circular');
  });

  test('should prevent multi-level circular references', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create A -> B -> C -> D hierarchy
    const categoryAResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Category A'
      });

    const categoryBResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Category B',
        parent_id: categoryAResponse.body.id
      });

    const categoryCResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Category C',
        parent_id: categoryBResponse.body.id
      });

    const categoryDResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Category D',
        parent_id: categoryCResponse.body.id
      });

    expect(categoryAResponse.status).toBe(201);
    expect(categoryBResponse.status).toBe(201);
    expect(categoryCResponse.status).toBe(201);
    expect(categoryDResponse.status).toBe(201);

    // Try to make B a child of D (B->C->D->B circular)
    const circularResponse = await request(app)
      .put(`/categories/${categoryBResponse.body.id}`)
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        parent_id: categoryDResponse.body.id
      });

    expect(circularResponse.status).toBe(400);
    expect(circularResponse.body.error.message).toContain('circular');
  });

  test('should allow valid parent changes', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create separate hierarchies A->B and C->D
    const categoryAResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Category A'
      });

    const categoryBResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Category B',
        parent_id: categoryAResponse.body.id
      });

    const categoryCResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Category C'
      });

    const categoryDResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Category D',
        parent_id: categoryCResponse.body.id
      });

    // Move B from A to C (valid move: A->B becomes C->B)
    const validMoveResponse = await request(app)
      .put(`/categories/${categoryBResponse.body.id}`)
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        parent_id: categoryCResponse.body.id
      });

    expect(validMoveResponse.status).toBe(200);
    expect(validMoveResponse.body.parent_id).toBe(categoryCResponse.body.id);

    // Verify the move was successful
    const hierarchyResponse = await request(app)
      .get(`/categories/${categoryBResponse.body.id}/hierarchy`);

    expect(hierarchyResponse.status).toBe(200);
    expect(hierarchyResponse.body.ancestors).toHaveLength(1);
    expect(hierarchyResponse.body.ancestors[0].name).toBe('Category C');
  });

  test('should validate against creating circular reference on category creation', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Try to create a category with non-existent parent (should fail gracefully)
    const nonExistentParentResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Invalid Category',
        parent_id: 999999
      });

    expect(nonExistentParentResponse.status).toBe(400);
    expect(nonExistentParentResponse.body.error.message).toContain('not found');
  });
});