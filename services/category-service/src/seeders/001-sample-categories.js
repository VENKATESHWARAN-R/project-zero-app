'use strict';

module.exports = {
  up: async (queryInterface, Sequelize) => {
    const now = new Date();

    await queryInterface.bulkInsert('categories', [
      {
        id: 1,
        name: 'Electronics',
        slug: 'electronics',
        description: 'Electronic devices and accessories',
        parent_id: null,
        sort_order: 10,
        is_active: true,
        created_at: now,
        updated_at: now,
      },
      {
        id: 2,
        name: 'Computers',
        slug: 'computers',
        description: 'Desktop and laptop computers',
        parent_id: 1,
        sort_order: 10,
        is_active: true,
        created_at: now,
        updated_at: now,
      },
      {
        id: 3,
        name: 'Laptops',
        slug: 'laptops',
        description: 'Portable computers',
        parent_id: 2,
        sort_order: 10,
        is_active: true,
        created_at: now,
        updated_at: now,
      },
      {
        id: 4,
        name: 'Gaming Laptops',
        slug: 'gaming-laptops',
        description: 'High-performance gaming laptops',
        parent_id: 3,
        sort_order: 10,
        is_active: true,
        created_at: now,
        updated_at: now,
      },
      {
        id: 5,
        name: 'Mobile Devices',
        slug: 'mobile-devices',
        description: 'Smartphones, tablets, and accessories',
        parent_id: 1,
        sort_order: 20,
        is_active: true,
        created_at: now,
        updated_at: now,
      },
      {
        id: 6,
        name: 'Smartphones',
        slug: 'smartphones',
        description: 'Mobile phones and accessories',
        parent_id: 5,
        sort_order: 10,
        is_active: true,
        created_at: now,
        updated_at: now,
      },
    ]);
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.bulkDelete('categories', null, {});
  },
};