#!/usr/bin/env node
/**
 * Database initialization script for Notification Service.
 * Creates tables and seeds test data for integration testing.
 * 
 * Run from notification-service directory:
 *     node scripts/init_db.js
 */

const path = require('path');

console.log('Starting Notification Service database initialization...');

async function initializeDatabase() {
  try {
    // Import database modules
    const { initializeDatabase: initDB, syncDatabase } = require(path.join(__dirname, '..', 'src', 'config', 'database'));
    
    console.log('Initializing database connection...');
    const sequelize = initDB();
    
    console.log('Creating database schema...');
    
    // Sync database schema
    await syncDatabase();
    console.log('Database schema created successfully');
    
    // Test database connection
    await sequelize.authenticate();
    console.log('Database connection verified');
    
    // Close connection
    await sequelize.close();
    
    console.log('Notification Service database initialization completed successfully');
    
  } catch (error) {
    console.error('Database initialization failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run initialization
initializeDatabase();