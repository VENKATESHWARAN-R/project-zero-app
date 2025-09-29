const swaggerJSDoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');
const fs = require('fs');
const path = require('path');

const options = {
  definition: {
    openapi: '3.0.3',
    info: {
      title: 'Category Management Service API',
      version: '1.0.0',
      description: 'Hierarchical category management for e-commerce product organization',
      contact: {
        name: 'Project Zero App Team',
      },
    },
    servers: [
      {
        url: 'http://localhost:8005',
        description: 'Local development server',
      },
      {
        url: 'http://category-service:8005',
        description: 'Docker container',
      },
    ],
    components: {
      securitySchemes: {
        BearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
          description: 'JWT token from auth service',
        },
      },
    },
  },
  apis: [
    path.join(__dirname, '../routes/*.js'),
    path.join(__dirname, './schemas.js'),
  ],
};

const specs = swaggerJSDoc(options);

// Save swagger.json to service root
const saveSwaggerJson = () => {
  const swaggerPath = path.join(__dirname, '../../swagger.json');
  fs.writeFileSync(swaggerPath, JSON.stringify(specs, null, 2));
  console.log('swagger.json saved to service root');
};

const setupSwagger = (app) => {
  // Generate and save swagger.json
  saveSwaggerJson();

  // Serve swagger documentation
  app.use('/docs', swaggerUi.serve, swaggerUi.setup(specs, {
    explorer: true,
    customCss: '.swagger-ui .topbar { display: none }',
    customSiteTitle: 'Category Service API Documentation',
  }));

  // Serve swagger.json
  app.get('/swagger.json', (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.send(specs);
  });
};

module.exports = {
  setupSwagger,
  saveSwaggerJson,
  specs,
};