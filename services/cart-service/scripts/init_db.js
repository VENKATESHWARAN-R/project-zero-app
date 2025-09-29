#!/usr/bin/env node
/**
 * Database initialization script for Cart Service.
 * Creates tables and seeds test data for integration testing.
 * 
 * Run from cart-service directory:
 *     node scripts/init_db.js
 */

const path = require('path');
const fs = require('fs');

// Add src directory to require path
const srcPath = path.join(__dirname, '..', 'src');

console.log('Starting Cart Service database initialization...');

async function initializeDatabase() {
  try {
    // Import database modules
    const { createSequelizeInstance } = require(path.join(srcPath, 'config', 'database'));
    const sequelize = createSequelizeInstance();
    
    // Import models to register them with Sequelize
    require(path.join(srcPath, 'models'));
    
    console.log('Creating database schema...');
    
    // Sync database schema
    await sequelize.sync({ force: false });
    console.log('Database schema created successfully');
    
    // Test database connection
    await sequelize.authenticate();
    console.log('Database connection verified');
    
    // Close connection
    await sequelize.close();
    
    console.log('Cart Service database initialization completed successfully');
    
  } catch (error) {
    console.error('Database initialization failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run initialization
initializeDatabase();