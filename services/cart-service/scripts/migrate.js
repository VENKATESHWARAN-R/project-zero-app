const { sequelize } = require('../src/models');

async function runMigrations() {
  try {
    console.log('Testing database connection...');
    await sequelize.authenticate();
    console.log('Database connection established successfully.');

    console.log('Running migrations...');
    await sequelize.sync({ force: false });
    console.log('Migrations completed successfully.');

    process.exit(0);
  } catch (error) {
    console.error('Migration failed:', error);
    process.exit(1);
  }
}

runMigrations();
