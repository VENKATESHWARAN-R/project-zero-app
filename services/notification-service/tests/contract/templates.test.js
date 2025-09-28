const request = require('supertest');
const app = require('../../src/app');

describe('Template Endpoints Contract Tests', () => {
  const validJWT = 'Bearer valid-jwt-token'; // Mock JWT for testing
  const adminJWT = 'Bearer admin-jwt-token'; // Mock admin JWT for testing
  const validTemplateId = '123e4567-e89b-12d3-a456-426614174000';

  describe('GET /templates', () => {
    it('should return 200 with templates list', async() => {
      const response = await request(app)
        .get('/templates')
        .set('Authorization', validJWT)
        .expect(200);

      expect(response.body).toMatchObject({
        templates: expect.arrayContaining([
          expect.objectContaining({
            id: expect.toBeValidUUID(),
            name: expect.any(String),
            type: expect.stringMatching(/^(welcome|order|payment|system|promotional)$/),
            channel: expect.stringMatching(/^(email|sms|in_app)$/),
            content: expect.any(String),
            isActive: expect.any(Boolean),
            createdAt: expect.any(String),
            updatedAt: expect.any(String),
          }),
        ]),
      });
    });

    it('should return 401 for missing authorization', async() => {
      const response = await request(app)
        .get('/templates')
        .expect(401);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
      });
    });

    it('should support filtering by type', async() => {
      const response = await request(app)
        .get('/templates?type=welcome')
        .set('Authorization', validJWT)
        .expect(200);

      expect(response.body).toMatchObject({
        templates: expect.any(Array),
      });

      // All templates should be welcome type if any exist
      if (response.body.templates.length > 0) {
        response.body.templates.forEach(template => {
          expect(template.type).toBe('welcome');
        });
      }
    });

    it('should support filtering by channel', async() => {
      const response = await request(app)
        .get('/templates?channel=email')
        .set('Authorization', validJWT)
        .expect(200);

      expect(response.body).toMatchObject({
        templates: expect.any(Array),
      });

      // All templates should be email channel if any exist
      if (response.body.templates.length > 0) {
        response.body.templates.forEach(template => {
          expect(template.channel).toBe('email');
        });
      }
    });

    it('should support filtering by active status', async() => {
      const response = await request(app)
        .get('/templates?active=true')
        .set('Authorization', validJWT)
        .expect(200);

      expect(response.body).toMatchObject({
        templates: expect.any(Array),
      });

      // All templates should be active if any exist
      if (response.body.templates.length > 0) {
        response.body.templates.forEach(template => {
          expect(template.isActive).toBe(true);
        });
      }
    });
  });

  describe('POST /templates', () => {
    const validTemplateRequest = {
      name: 'test_email_notification',
      type: 'system',
      channel: 'email',
      subject: 'Test Template Subject',
      content: 'Hello {{userName}}, this is a test notification.',
      variables: {
        userName: { type: 'string', required: true },
      },
      isActive: true,
    };

    it('should return 201 with created template for admin user', async() => {
      const response = await request(app)
        .post('/templates')
        .set('Authorization', adminJWT)
        .send(validTemplateRequest)
        .expect(201);

      expect(response.body).toMatchObject({
        id: expect.toBeValidUUID(),
        name: 'test_email_notification',
        type: 'system',
        channel: 'email',
        subject: 'Test Template Subject',
        content: 'Hello {{userName}}, this is a test notification.',
        variables: {
          userName: { type: 'string', required: true },
        },
        isActive: true,
        createdAt: expect.any(String),
        updatedAt: expect.any(String),
      });
    });

    it('should return 401 for missing authorization', async() => {
      const response = await request(app)
        .post('/templates')
        .send(validTemplateRequest)
        .expect(401);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
      });
    });

    it('should return 403 for non-admin user', async() => {
      const response = await request(app)
        .post('/templates')
        .set('Authorization', validJWT)
        .send(validTemplateRequest)
        .expect(403);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('admin'),
      });
    });

    it('should return 422 for missing required fields', async() => {
      const invalidRequest = { name: 'incomplete' };

      const response = await request(app)
        .post('/templates')
        .set('Authorization', adminJWT)
        .send(invalidRequest)
        .expect(422);

      expect(response.body).toMatchObject({
        error: 'validation_error',
        message: expect.any(String),
        errors: expect.arrayContaining([
          expect.objectContaining({
            field: expect.any(String),
            message: expect.any(String),
          }),
        ]),
      });
    });

    it('should return 400 for invalid template name format', async() => {
      const invalidRequest = {
        ...validTemplateRequest,
        name: 'InvalidTemplateName',
      };

      const response = await request(app)
        .post('/templates')
        .set('Authorization', adminJWT)
        .send(invalidRequest)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('name'),
      });
    });

    it('should return 400 for duplicate template name', async() => {
      const duplicateRequest = {
        ...validTemplateRequest,
        name: 'welcome_email_registration', // Assuming this exists
      };

      const response = await request(app)
        .post('/templates')
        .set('Authorization', adminJWT)
        .send(duplicateRequest)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('already exists'),
      });
    });
  });

  describe('GET /templates/:id', () => {
    it('should return 200 with template details for valid ID', async() => {
      const response = await request(app)
        .get(`/templates/${validTemplateId}`)
        .set('Authorization', validJWT)
        .expect(200);

      expect(response.body).toMatchObject({
        id: validTemplateId,
        name: expect.any(String),
        type: expect.stringMatching(/^(welcome|order|payment|system|promotional)$/),
        channel: expect.stringMatching(/^(email|sms|in_app)$/),
        content: expect.any(String),
        isActive: expect.any(Boolean),
        createdAt: expect.any(String),
        updatedAt: expect.any(String),
      });
    });

    it('should return 401 for missing authorization', async() => {
      const response = await request(app)
        .get(`/templates/${validTemplateId}`)
        .expect(401);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
      });
    });

    it('should return 404 for non-existent template', async() => {
      const nonExistentId = '999e4567-e89b-12d3-a456-426614174999';

      const response = await request(app)
        .get(`/templates/${nonExistentId}`)
        .set('Authorization', validJWT)
        .expect(404);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
        path: `/templates/${nonExistentId}`,
      });
    });

    it('should return 400 for invalid UUID format', async() => {
      const invalidId = 'invalid-uuid';

      const response = await request(app)
        .get(`/templates/${invalidId}`)
        .set('Authorization', validJWT)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
      });
    });
  });

  describe('PUT /templates/:id', () => {
    const validUpdateRequest = {
      subject: 'Updated Subject',
      content: 'Updated content for {{userName}}',
      variables: {
        userName: { type: 'string', required: true },
        newField: { type: 'string', required: false },
      },
      isActive: false,
    };

    it('should return 200 with updated template for admin user', async() => {
      const response = await request(app)
        .put(`/templates/${validTemplateId}`)
        .set('Authorization', adminJWT)
        .send(validUpdateRequest)
        .expect(200);

      expect(response.body).toMatchObject({
        id: validTemplateId,
        subject: 'Updated Subject',
        content: 'Updated content for {{userName}}',
        variables: {
          userName: { type: 'string', required: true },
          newField: { type: 'string', required: false },
        },
        isActive: false,
        updatedAt: expect.any(String),
      });

      // UpdatedAt should be different from createdAt
      expect(response.body.updatedAt).not.toBe(response.body.createdAt);
    });

    it('should return 401 for missing authorization', async() => {
      const response = await request(app)
        .put(`/templates/${validTemplateId}`)
        .send(validUpdateRequest)
        .expect(401);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
      });
    });

    it('should return 403 for non-admin user', async() => {
      const response = await request(app)
        .put(`/templates/${validTemplateId}`)
        .set('Authorization', validJWT)
        .send(validUpdateRequest)
        .expect(403);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.stringContaining('admin'),
      });
    });

    it('should return 404 for non-existent template', async() => {
      const nonExistentId = '999e4567-e89b-12d3-a456-426614174999';

      const response = await request(app)
        .put(`/templates/${nonExistentId}`)
        .set('Authorization', adminJWT)
        .send(validUpdateRequest)
        .expect(404);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
        path: `/templates/${nonExistentId}`,
      });
    });

    it('should return 400 for invalid UUID format', async() => {
      const invalidId = 'invalid-uuid';

      const response = await request(app)
        .put(`/templates/${invalidId}`)
        .set('Authorization', adminJWT)
        .send(validUpdateRequest)
        .expect(400);

      expect(response.body).toMatchObject({
        error: expect.any(String),
        message: expect.any(String),
      });
    });

    it('should allow partial updates', async() => {
      const partialUpdate = { isActive: true };

      const response = await request(app)
        .put(`/templates/${validTemplateId}`)
        .set('Authorization', adminJWT)
        .send(partialUpdate)
        .expect(200);

      expect(response.body).toMatchObject({
        id: validTemplateId,
        isActive: true,
        updatedAt: expect.any(String),
      });
    });
  });
});