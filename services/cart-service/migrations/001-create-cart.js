const { DataTypes } = require('sequelize');

module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.createTable('Cart', {
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
      },
      user_id: {
        type: DataTypes.STRING,
        allowNull: false,
      },
      created_at: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW,
        allowNull: false,
      },
      updated_at: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW,
        allowNull: false,
      },
    });

    // Add indexes
    await queryInterface.addIndex('Cart', ['user_id'], {
      name: 'idx_cart_user_id',
    });

    await queryInterface.addIndex('Cart', ['updated_at'], {
      name: 'idx_cart_updated_at',
    });
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.dropTable('Cart');
  },
};
