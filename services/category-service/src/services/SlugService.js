const { Category } = require('../models');
const { Op } = require('sequelize');

class SlugService {
  // Generate slug from name
  static generateSlug(name) {
    if (!name || typeof name !== 'string') {
      throw new Error('Name is required to generate slug');
    }

    return name
      .toLowerCase()
      .trim()
      // Replace spaces and underscores with hyphens
      .replace(/[\s_]+/g, '-')
      // Remove special characters except hyphens
      .replace(/[^a-z0-9-]/g, '')
      // Remove multiple consecutive hyphens
      .replace(/-+/g, '-')
      // Remove leading and trailing hyphens
      .replace(/^-+|-+$/g, '')
      // Ensure minimum length
      .substring(0, 120) || 'category';
  }

  // Check if slug exists
  static async slugExists(slug, excludeId = null) {
    const whereClause = { slug };

    if (excludeId) {
      whereClause.id = { [Op.ne]: excludeId };
    }

    const existingCategory = await Category.findOne({
      where: whereClause,
      attributes: ['id']
    });

    return !!existingCategory;
  }

  // Generate unique slug
  static async generateUniqueSlug(name, excludeId = null) {
    const baseSlug = this.generateSlug(name);
    let slug = baseSlug;
    let counter = 1;

    // Keep checking until we find a unique slug
    while (await this.slugExists(slug, excludeId)) {
      slug = `${baseSlug}-${counter}`;
      counter++;

      // Prevent infinite loops
      if (counter > 1000) {
        slug = `${baseSlug}-${Date.now()}`;
        break;
      }
    }

    return slug;
  }

  // Update slug for existing category
  static async updateSlug(categoryId, newName) {
    const category = await Category.findByPk(categoryId);
    if (!category) {
      throw new Error('Category not found');
    }

    const newSlug = await this.generateUniqueSlug(newName, categoryId);

    await category.update({ slug: newSlug });

    return newSlug;
  }

  // Validate slug format
  static validateSlug(slug) {
    if (!slug || typeof slug !== 'string') {
      throw new Error('Slug is required and must be a string');
    }

    const trimmedSlug = slug.trim();

    if (trimmedSlug.length === 0) {
      throw new Error('Slug cannot be empty');
    }

    if (trimmedSlug.length > 120) {
      throw new Error('Slug cannot exceed 120 characters');
    }

    // Check slug format - only lowercase letters, numbers, and hyphens
    const slugPattern = /^[a-z0-9-]+$/;
    if (!slugPattern.test(trimmedSlug)) {
      throw new Error('Slug can only contain lowercase letters, numbers, and hyphens');
    }

    // Cannot start or end with hyphen
    if (trimmedSlug.startsWith('-') || trimmedSlug.endsWith('-')) {
      throw new Error('Slug cannot start or end with a hyphen');
    }

    // Cannot have consecutive hyphens
    if (trimmedSlug.includes('--')) {
      throw new Error('Slug cannot contain consecutive hyphens');
    }

    return trimmedSlug;
  }

  // Generate slug with hierarchy path
  static async generateHierarchicalSlug(categoryId) {
    const category = await Category.findByPk(categoryId, {
      include: [{
        model: Category,
        as: 'parent',
        include: [{
          model: Category,
          as: 'parent',
          include: [{
            model: Category,
            as: 'parent',
            include: [{
              model: Category,
              as: 'parent',
              include: [{
                model: Category,
                as: 'parent'
              }]
            }]
          }]
        }]
      }]
    });

    if (!category) {
      throw new Error('Category not found');
    }

    const pathParts = [];
    let current = category;

    // Build path from category to root
    while (current) {
      pathParts.unshift(current.slug || this.generateSlug(current.name));
      current = current.parent;
    }

    return pathParts.join('/');
  }

  // Find category by slug
  static async findBySlug(slug) {
    const validatedSlug = this.validateSlug(slug);

    const category = await Category.findOne({
      where: { slug: validatedSlug, is_active: true }
    });

    return category;
  }

  // Find category by hierarchical slug path
  static async findBySlugPath(slugPath) {
    if (!slugPath || typeof slugPath !== 'string') {
      throw new Error('Slug path is required');
    }

    const slugParts = slugPath.split('/').filter(part => part.length > 0);

    if (slugParts.length === 0) {
      throw new Error('Invalid slug path');
    }

    // Validate each slug part
    slugParts.forEach(slug => this.validateSlug(slug));

    let currentCategory = null;
    let parentId = null;

    // Find each category in the path
    for (const slug of slugParts) {
      currentCategory = await Category.findOne({
        where: {
          slug,
          parent_id: parentId,
          is_active: true
        }
      });

      if (!currentCategory) {
        return null; // Path not found
      }

      parentId = currentCategory.id;
    }

    return currentCategory;
  }

  // Generate breadcrumb slugs for category hierarchy
  static async generateBreadcrumbSlugs(categoryId) {
    const category = await Category.findByPk(categoryId);
    if (!category) {
      throw new Error('Category not found');
    }

    const breadcrumbs = [];
    const ancestors = await category.getAncestors();

    // Add ancestors
    for (const ancestor of ancestors) {
      breadcrumbs.push({
        id: ancestor.id,
        name: ancestor.name,
        slug: ancestor.slug
      });
    }

    // Add current category
    breadcrumbs.push({
      id: category.id,
      name: category.name,
      slug: category.slug
    });

    return breadcrumbs;
  }

  // Bulk update slugs for all categories
  static async updateAllSlugs() {
    const categories = await Category.findAll({
      order: [['id', 'ASC']]
    });

    const updatePromises = categories.map(async (category) => {
      try {
        const newSlug = await this.generateUniqueSlug(category.name, category.id);
        if (newSlug !== category.slug) {
          await category.update({ slug: newSlug });
          return {
            id: category.id,
            name: category.name,
            oldSlug: category.slug,
            newSlug
          };
        }
        return null;
      } catch (error) {
        return {
          id: category.id,
          name: category.name,
          error: error.message
        };
      }
    });

    const results = await Promise.all(updatePromises);
    return results.filter(result => result !== null);
  }

  // Get slug suggestions based on name
  static getSluggSuggestions(name, maxSuggestions = 5) {
    if (!name || typeof name !== 'string') {
      return [];
    }

    const baseSlug = this.generateSlug(name);
    const suggestions = [baseSlug];

    // Generate variations
    const words = name.toLowerCase().split(/\s+/);

    if (words.length > 1) {
      // Use first word only
      suggestions.push(this.generateSlug(words[0]));

      // Use last word only
      suggestions.push(this.generateSlug(words[words.length - 1]));

      // Use initials
      const initials = words.map(word => word.charAt(0)).join('');
      suggestions.push(this.generateSlug(initials));

      // Use first and last word
      if (words.length > 2) {
        suggestions.push(this.generateSlug(`${words[0]} ${words[words.length - 1]}`));
      }
    }

    // Remove duplicates and limit results
    return [...new Set(suggestions)].slice(0, maxSuggestions);
  }

  // Validate and sanitize category name for slug generation
  static sanitizeNameForSlug(name) {
    if (!name || typeof name !== 'string') {
      throw new Error('Name is required for slug generation');
    }

    // Remove HTML tags
    const cleanName = name.replace(/<[^>]*>/g, '');

    // Remove excessive whitespace
    const trimmedName = cleanName.replace(/\s+/g, ' ').trim();

    if (trimmedName.length === 0) {
      throw new Error('Name cannot be empty after sanitization');
    }

    return trimmedName;
  }

  // Check slug availability
  static async checkSlugAvailability(slug, excludeId = null) {
    try {
      const validatedSlug = this.validateSlug(slug);
      const exists = await this.slugExists(validatedSlug, excludeId);

      return {
        slug: validatedSlug,
        available: !exists,
        suggestions: exists ? this.getSluggSuggestions(slug) : []
      };
    } catch (error) {
      return {
        slug,
        available: false,
        error: error.message,
        suggestions: []
      };
    }
  }
}

module.exports = SlugService;