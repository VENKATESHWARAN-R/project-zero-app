const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const CartItem = sequelize.define(
    'CartItem',
    {
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
      },
      cart_id: {
        type: DataTypes.UUID,
        allowNull: false,
        references: {
          model: 'Cart',
          key: 'id',
        },
        index: true,
      },
      product_id: {
        type: DataTypes.STRING,
        allowNull: false,
        index: true,
      },
      quantity: {
        type: DataTypes.INTEGER,
        allowNull: false,
        validate: {
          min: 1,
          max: 10,
        },
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
      tableName: 'CartItem',
      timestamps: true,
      createdAt: 'created_at',
      updatedAt: 'updated_at',
      indexes: [
        {
          name: 'idx_cartitem_cart_id',
          fields: ['cart_id'],
        },
        {
          name: 'idx_cartitem_product_id',
          fields: ['product_id'],
        },
        {
          name: 'idx_cartitem_unique',
          unique: true,
          fields: ['cart_id', 'product_id'],
        },
      ],
    }
  );

  CartItem.associate = (models) => {
    CartItem.belongsTo(models.Cart, {
      foreignKey: 'cart_id',
      as: 'cart',
    });
  };

  return CartItem;
};
