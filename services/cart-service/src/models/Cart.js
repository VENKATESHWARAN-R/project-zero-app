const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const Cart = sequelize.define(
    'Cart',
    {
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
      },
      user_id: {
        type: DataTypes.STRING,
        allowNull: false,
        index: true,
      },
      created_at: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW,
        field: 'created_at',
      },
      updated_at: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW,
        field: 'updated_at',
      },
    },
    {
      tableName: 'Cart',
      timestamps: true,
      createdAt: 'created_at',
      updatedAt: 'updated_at',
      indexes: [
        {
          name: 'idx_cart_user_id',
          fields: ['user_id'],
        },
        {
          name: 'idx_cart_updated_at',
          fields: ['updated_at'],
        },
      ],
    }
  );

  Cart.associate = (models) => {
    Cart.hasMany(models.CartItem, {
      foreignKey: 'cart_id',
      as: 'items',
      onDelete: 'CASCADE',
    });
  };

  return Cart;
};
