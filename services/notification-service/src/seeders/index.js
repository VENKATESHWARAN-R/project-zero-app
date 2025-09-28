const { sequelize } = require('../models');
const { seedDefaultTemplates } = require('./defaultTemplates');

async function runSeeder() {
  try {
    console.log('Starting database seeder...');

    // Ensure database connection
    await sequelize.authenticate();
    console.log('Database connection established.');

    // Sync models (create tables if they don't exist)
    await sequelize.sync();
    console.log('Database models synchronized.');

    // Seed default templates
    await seedDefaultTemplates();

    console.log('Database seeding completed successfully!');
    process.exit(0);
  } catch (error) {
    console.error('Database seeding failed:', error);
    process.exit(1);
  }
}

// Run seeder if this file is executed directly
if (require.main === module) {
  runSeeder();
}

module.exports = {
  runSeeder,
  seedDefaultTemplates
};