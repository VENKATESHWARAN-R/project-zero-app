const fs = require('fs');
const path = require('path');
const swaggerJSDocs = require('./docs');

// Function to generate and save swagger.json
function generateSwaggerJson() {
  try {
    // Use the comprehensive swagger documentation from docs.js
    const swaggerDocument = swaggerJSDocs;

    // Save to swagger.json file
    const outputPath = path.join(__dirname, '../../swagger.json');
    fs.writeFileSync(outputPath, JSON.stringify(swaggerDocument, null, 2));

    console.log('Swagger documentation generated successfully at:', outputPath);
    return swaggerDocument;
  } catch (error) {
    console.error('Error generating Swagger documentation:', error);
    throw error;
  }
}

module.exports = {
  generateSwaggerJson,
  swaggerJSDocs
};