const request = require('supertest');
const { Category } = require('../../src/models');
const { sequelize } = require('../../src/models');

describe('Category Hierarchy Integration Tests', () => {
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

  test('should create and manage 5-level category hierarchy', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Level 1: Electronics
    const level1Response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Electronics',
        description: 'Electronic devices'
      });

    expect(level1Response.status).toBe(201);
    const level1Id = level1Response.body.id;

    // Level 2: Computers
    const level2Response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Computers',
        description: 'Computing devices',
        parent_id: level1Id
      });

    expect(level2Response.status).toBe(201);
    const level2Id = level2Response.body.id;

    // Level 3: Laptops
    const level3Response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Laptops',
        description: 'Portable computers',
        parent_id: level2Id
      });

    expect(level3Response.status).toBe(201);
    const level3Id = level3Response.body.id;

    // Level 4: Gaming Laptops
    const level4Response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Gaming Laptops',
        description: 'Gaming computers',
        parent_id: level3Id
      });

    expect(level4Response.status).toBe(201);
    const level4Id = level4Response.body.id;

    // Level 5: High-End Gaming Laptops
    const level5Response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'High-End Gaming Laptops',
        description: 'Premium gaming laptops',
        parent_id: level4Id
      });

    expect(level5Response.status).toBe(201);
    const level5Id = level5Response.body.id;

    // Verify hierarchy structure
    const hierarchyResponse = await request(app)
      .get(`/categories/${level5Id}/hierarchy`);

    expect(hierarchyResponse.status).toBe(200);
    expect(hierarchyResponse.body.depth).toBe(4);
    expect(hierarchyResponse.body.ancestors).toHaveLength(4);
    expect(hierarchyResponse.body.ancestors[0].name).toBe('Electronics');
    expect(hierarchyResponse.body.ancestors[3].name).toBe('Gaming Laptops');
  });

  test('should validate hierarchy depth limits', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create 5-level hierarchy (max allowed)
    let parentId = null;
    const categoryIds = [];

    for (let i = 1; i <= 5; i++) {
      const response = await request(app)
        .post('/categories')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          name: `Level ${i} Category`,
          parent_id: parentId
        });

      expect(response.status).toBe(201);
      parentId = response.body.id;
      categoryIds.push(parentId);
    }

    // Try to create 6th level - should fail
    const level6Response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Level 6 Category',
        parent_id: parentId
      });

    expect(level6Response.status).toBe(400);
    expect(level6Response.body.error.message).toContain('depth');
  });

  test('should handle category movement between parents', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create root categories
    const parent1Response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Parent 1',
        description: 'First parent category'
      });

    const parent2Response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Parent 2',
        description: 'Second parent category'
      });

    // Create child under parent 1
    const childResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Movable Child',
        description: 'Child that will be moved',
        parent_id: parent1Response.body.id
      });

    expect(childResponse.status).toBe(201);
    const childId = childResponse.body.id;

    // Move child from parent 1 to parent 2
    const moveResponse = await request(app)
      .put(`/categories/${childId}`)
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        parent_id: parent2Response.body.id
      });

    expect(moveResponse.status).toBe(200);
    expect(moveResponse.body.parent_id).toBe(parent2Response.body.id);

    // Verify the move in hierarchy
    const hierarchyResponse = await request(app)
      .get(`/categories/${childId}/hierarchy`);

    expect(hierarchyResponse.status).toBe(200);
    expect(hierarchyResponse.body.ancestors).toHaveLength(1);
    expect(hierarchyResponse.body.ancestors[0].name).toBe('Parent 2');
  });

  test('should get complete category tree structure', async () => {
    if (!app) {
      throw new Error('App not implemented yet - this test should fail');
    }

    // Create test hierarchy
    const rootResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ name: 'Root Category' });

    const child1Response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Child 1',
        parent_id: rootResponse.body.id
      });

    const child2Response = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Child 2',
        parent_id: rootResponse.body.id
      });

    const grandchildResponse = await request(app)
      .post('/categories')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        name: 'Grandchild',
        parent_id: child1Response.body.id
      });

    // Get categories with children
    const treeResponse = await request(app)
      .get('/categories')
      .query({
        parent_id: null,
        include_children: true
      });

    expect(treeResponse.status).toBe(200);
    expect(treeResponse.body.categories).toHaveLength(1);

    const rootCategory = treeResponse.body.categories[0];
    expect(rootCategory.name).toBe('Root Category');
    expect(rootCategory.children).toHaveLength(2);

    const child1 = rootCategory.children.find(c => c.name === 'Child 1');
    expect(child1).toBeDefined();
  });
});