'use strict';

module.exports = {
  up: async (queryInterface, Sequelize) => {
    // Performance indexes
    await queryInterface.addIndex('categories', {
      fields: ['parent_id'],
      name: 'idx_categories_parent_id',
    });

    await queryInterface.addIndex('categories', {
      fields: ['slug'],
      name: 'idx_categories_slug',
    });

    await queryInterface.addIndex('categories', {
      fields: ['is_active'],
      name: 'idx_categories_active',
    });

    await queryInterface.addIndex('categories', {
      fields: ['parent_id', 'sort_order'],
      name: 'idx_categories_sort_order',
    });

    await queryInterface.addIndex('categories', {
      fields: ['name'],
      name: 'idx_categories_name',
    });

    // Unique constraint for name within parent scope
    await queryInterface.addIndex('categories', {
      fields: ['name', 'parent_id'],
      unique: true,
      name: 'categories_name_parent_unique',
    });
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.removeIndex('categories', 'idx_categories_parent_id');
    await queryInterface.removeIndex('categories', 'idx_categories_slug');
    await queryInterface.removeIndex('categories', 'idx_categories_active');
    await queryInterface.removeIndex('categories', 'idx_categories_sort_order');
    await queryInterface.removeIndex('categories', 'idx_categories_name');
    await queryInterface.removeIndex('categories', 'categories_name_parent_unique');
  },
};