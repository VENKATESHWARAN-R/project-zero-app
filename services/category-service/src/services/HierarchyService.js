const { Category } = require('../models');

class HierarchyService {
  static MAX_DEPTH = 5;

  // Validate hierarchy constraints
  static async validateHierarchy(categoryId, newParentId) {
    if (!newParentId) return true; // Root category is valid

    if (newParentId === categoryId) {
      throw new Error('Category cannot be its own parent');
    }

    // Check if category exists
    const category = await Category.findByPk(categoryId);
    if (!category) {
      throw new Error('Category not found');
    }

    // Check if parent exists
    const parent = await Category.findByPk(newParentId);
    if (!parent) {
      throw new Error('Parent category not found');
    }

    // Check if newParentId would create a circular reference
    const isDescendant = await this.isDescendantOf(newParentId, categoryId);
    if (isDescendant) {
      throw new Error('Cannot create circular hierarchy');
    }

    // Check depth limit
    const parentDepth = await this.getCategoryDepth(newParentId);
    if (parentDepth >= this.MAX_DEPTH - 1) {
      throw new Error(`Maximum hierarchy depth of ${this.MAX_DEPTH} exceeded`);
    }

    return true;
  }

  // Check if a category is a descendant of another
  static async isDescendantOf(categoryId, ancestorId) {
    const descendants = await this.getAllDescendants(ancestorId);
    return descendants.some(desc => desc.id === categoryId);
  }

  // Get all descendants of a category
  static async getAllDescendants(categoryId, visited = new Set()) {
    if (visited.has(categoryId)) {
      return []; // Prevent infinite recursion
    }
    visited.add(categoryId);

    const children = await Category.findAll({
      where: { parent_id: categoryId },
      attributes: ['id', 'name', 'parent_id'],
    });

    const descendants = [...children];

    for (const child of children) {
      const grandChildren = await this.getAllDescendants(child.id, visited);
      descendants.push(...grandChildren);
    }

    return descendants;
  }

  // Get category depth in hierarchy
  static async getCategoryDepth(categoryId) {
    let depth = 0;
    let currentId = categoryId;

    while (currentId && depth < this.MAX_DEPTH) {
      const category = await Category.findByPk(currentId, {
        attributes: ['parent_id'],
      });

      if (!category || !category.parent_id) {
        break;
      }

      currentId = category.parent_id;
      depth++;
    }

    return depth;
  }

  // Get full path from root to category
  static async getCategoryPath(categoryId) {
    const path = [];
    let currentId = categoryId;

    while (currentId && path.length < this.MAX_DEPTH) {
      const category = await Category.findByPk(currentId, {
        attributes: ['id', 'name', 'parent_id'],
      });

      if (!category) {
        break;
      }

      path.unshift(category);
      currentId = category.parent_id;
    }

    return path;
  }

  // Move category to new parent
  static async moveCategory(categoryId, newParentId) {
    await this.validateHierarchy(categoryId, newParentId);

    const category = await Category.findByPk(categoryId);
    if (!category) {
      throw new Error('Category not found');
    }

    const oldParentId = category.parent_id;

    // Update the category
    await category.update({ parent_id: newParentId });

    return {
      category,
      old_parent_id: oldParentId,
      new_parent_id: newParentId,
    };
  }

  // Get category tree structure
  static async getCategoryTree(rootId = null, maxDepth = this.MAX_DEPTH) {
    const categories = await Category.findAll({
      where: { parent_id: rootId, is_active: true },
      order: [['sort_order', 'ASC'], ['name', 'ASC']],
    });

    if (maxDepth <= 1) {
      return categories.map(cat => cat.toJSON());
    }

    const tree = [];
    for (const category of categories) {
      const categoryData = category.toJSON();
      categoryData.children = await this.getCategoryTree(category.id, maxDepth - 1);
      tree.push(categoryData);
    }

    return tree;
  }

  // Reorder categories within same parent
  static async reorderCategories(parentId, categoryOrders) {
    // categoryOrders should be array of { id, sort_order }
    const updatePromises = categoryOrders.map(({ id, sort_order }) =>
      Category.update(
        { sort_order },
        {
          where: {
            id,
            parent_id: parentId,
          },
        }
      )
    );

    await Promise.all(updatePromises);

    return true;
  }

  // Validate entire hierarchy integrity
  static async validateHierarchyIntegrity() {
    const issues = [];

    // Check for circular references
    const allCategories = await Category.findAll({
      attributes: ['id', 'parent_id'],
    });

    for (const category of allCategories) {
      try {
        if (category.parent_id) {
          const depth = await this.getCategoryDepth(category.id);
          if (depth >= this.MAX_DEPTH) {
            issues.push({
              type: 'depth_exceeded',
              category_id: category.id,
              depth,
            });
          }

          const isCircular = await this.isDescendantOf(category.parent_id, category.id);
          if (isCircular) {
            issues.push({
              type: 'circular_reference',
              category_id: category.id,
              parent_id: category.parent_id,
            });
          }
        }
      } catch (error) {
        issues.push({
          type: 'validation_error',
          category_id: category.id,
          error: error.message,
        });
      }
    }

    return {
      is_valid: issues.length === 0,
      issues,
    };
  }
}

module.exports = HierarchyService;