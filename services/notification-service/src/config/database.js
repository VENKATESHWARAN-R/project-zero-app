const { Sequelize } = require('sequelize');
const config = require('./index');

let sequelize;

const initializeDatabase = () => {
  if (sequelize) {
    return sequelize;
  }

  const dbConfig = config.database;

  if (dbConfig.dialect === 'sqlite') {
    sequelize = new Sequelize({
      dialect: 'sqlite',
      storage: dbConfig.storage,
      logging: dbConfig.logging,
      pool: dbConfig.pool,
      define: {
        timestamps: true,
        paranoid: false,
        underscored: false,
        freezeTableName: true,
      },
    });
  } else {
    // For PostgreSQL or other databases
    sequelize = new Sequelize(dbConfig.url, {
      dialect: dbConfig.dialect,
      logging: dbConfig.logging,
      pool: dbConfig.pool,
      define: {
        timestamps: true,
        paranoid: false,
        underscored: false,
        freezeTableName: true,
      },
    });
  }

  return sequelize;
};

const testConnection = async() => {
  try {
    const db = initializeDatabase();
    await db.authenticate();
    console.log('Database connection has been established successfully.');
    return true;
  } catch (error) {
    console.error('Unable to connect to the database:', error);
    return false;
  }
};

const syncDatabase = async(options = {}) => {
  try {
    const db = initializeDatabase();
    await db.sync(options);
    console.log('Database synchronized successfully.');
    return true;
  } catch (error) {
    console.error('Error synchronizing database:', error);
    return false;
  }
};

const closeConnection = async() => {
  try {
    if (sequelize) {
      await sequelize.close();
      console.log('Database connection closed.');
    }
  } catch (error) {
    console.error('Error closing database connection:', error);
  }
};

module.exports = {
  sequelize: initializeDatabase(),
  initializeDatabase,
  testConnection,
  syncDatabase,
  closeConnection,
};