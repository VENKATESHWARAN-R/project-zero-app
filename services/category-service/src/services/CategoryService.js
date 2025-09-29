const { Category } = require('../models');
const { Op } = require('sequelize');

class CategoryService {
  // Create a new category
  static async createCategory(data) {
    const { name, description, image_url, parent_id, sort_order, metadata } = data;

    // Validate parent if provided
    if (parent_id) {
      const parent = await Category.findByPk(parent_id);
      if (!parent) {
        throw new Error('Parent category not found');
      }

      // Check depth limit
      const parentDepth = await parent.getDepth();
      if (parentDepth >= 4) { // Max depth is 5 (0-4)
        throw new Error('Maximum hierarchy depth exceeded');
      }
    }

    // Auto-assign sort order if not provided
    const finalSortOrder = sort_order !== undefined
      ? sort_order
      : await Category.getNextSortOrder(parent_id);

    const category = await Category.create({
      name,
      description,
      image_url,
      parent_id,
      sort_order: finalSortOrder,
      metadata,
    });

    return category;
  }

  // Get categories with filtering and optional hierarchy
  static async getCategories(options = {}) {
    const {
      parent_id,
      include_children = false,
      include_product_count = false,
      active_only = true,
    } = options;

    const whereClause = {};

    if (parent_id !== undefined && parent_id !== null) {
      whereClause.parent_id = parent_id;
    } else if (parent_id === null) {
      whereClause.parent_id = null;
    }

    if (active_only) {
      whereClause.is_active = true;
    }

    const includeOptions = [];

    if (include_children) {
      includeOptions.push({
        model: Category,
        as: 'children',
        where: active_only ? { is_active: true } : {},
        required: false,
        order: [['sort_order', 'ASC'], ['name', 'ASC']],
      });
    }

    const categories = await Category.findAll({
      where: whereClause,
      include: includeOptions,
      order: [['sort_order', 'ASC'], ['name', 'ASC']],
    });

    // Add product counts if requested
    if (include_product_count) {
      // This would integrate with product service
      // For now, return mock counts
      for (const category of categories) {
        category.dataValues.product_count = Math.floor(Math.random() * 50);
      }
    }

    return {
      categories,
      total: categories.length,
      filters: {
        parent_id,
        include_children,
        include_product_count,
        active_only,
      },
    };
  }

  // Get category by ID with optional includes
  static async getCategoryById(id, options = {}) {
    const {
      include_children = false,
      include_ancestors = false,
      include_product_count = false,
    } = options;

    const includeOptions = [];

    if (include_children) {
      includeOptions.push({
        model: Category,
        as: 'children',
        where: { is_active: true },
        required: false,
        order: [['sort_order', 'ASC'], ['name', 'ASC']],
      });
    }

    const category = await Category.findByPk(id, {
      include: includeOptions,
    });

    if (!category) {
      throw new Error('Category not found');
    }

    const result = category.toJSON();

    if (include_ancestors) {
      result.ancestors = await category.getAncestors();
      result.full_path = await category.getPath();
    }

    if (include_product_count) {
      result.product_count = Math.floor(Math.random() * 50);
    }

    return result;
  }

  // Update category
  static async updateCategory(id, data) {
    const category = await Category.findByPk(id);
    if (!category) {
      throw new Error('Category not found');
    }

    const { parent_id, ...otherData } = data;

    // Validate hierarchy if parent_id is being changed
    if (parent_id !== undefined && parent_id !== category.parent_id) {
      await category.validateHierarchy(parent_id);
    }

    await category.update({ parent_id, ...otherData });
    await category.reload();

    return category;
  }

  // Delete category
  static async deleteCategory(id, force = false) {
    const category = await Category.findByPk(id);
    if (!category) {
      throw new Error('Category not found');
    }

    // Check for active children
    const hasChildren = await category.hasActiveChildren();
    if (hasChildren && !force) {
      throw new Error('Cannot delete category with active children');
    }

    if (force) {
      // Soft delete by marking as inactive
      await category.update({ is_active: false });
    } else {
      // Hard delete
      await category.destroy();
    }

    return true;
  }

  // Get category hierarchy
  static async getCategoryHierarchy(id) {
    const category = await Category.findByPk(id);
    if (!category) {
      throw new Error('Category not found');
    }

    const ancestors = await category.getAncestors();
    const descendants = await category.getDescendants();
    const depth = await category.getDepth();

    return {
      category: category.toJSON(),
      ancestors: ancestors.map(cat => cat.toJSON()),
      descendants: descendants.map(cat => cat.toJSON()),
      depth,
      max_depth: 5,
    };
  }

  // Search categories
  static async searchCategories(query, options = {}) {
    const { active_only = true } = options;

    const whereClause = {
      [Op.or]: [
        { name: { [Op.like]: `%${query}%` } },
        { description: { [Op.like]: `%${query}%` } },
      ],
    };

    if (active_only) {
      whereClause.is_active = true;
    }

    const categories = await Category.findAll({
      where: whereClause,
      order: [['name', 'ASC']],
    });

    return {
      categories,
      query,
      total: categories.length,
    };
  }
}

module.exports = CategoryService;