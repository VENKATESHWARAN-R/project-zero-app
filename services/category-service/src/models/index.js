const { sequelize } = require('../config/database');
const Category = require('./Category');

// Initialize models
Category.init(sequelize);

// Set up associations
Category.associate({ Category });

module.exports = {
  sequelize,
  Category,
};