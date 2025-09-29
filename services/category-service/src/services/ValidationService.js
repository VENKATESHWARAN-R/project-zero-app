const { Category } = require('../models');
const { Op } = require('sequelize');
const HierarchyService = require('./HierarchyService');

class ValidationService {
  // Validate category name uniqueness within parent scope
  static async validateNameUniqueness(name, parentId, excludeId = null) {
    const whereClause = {
      name: {
        [Op.iLike]: name // Case-insensitive check
      },
      parent_id: parentId
    };

    // Exclude current category when updating
    if (excludeId) {
      whereClause.id = { [Op.ne]: excludeId };
    }

    const existingCategory = await Category.findOne({
      where: whereClause
    });

    if (existingCategory) {
      throw new Error(
        `Category name "${name}" already exists within this parent scope`
      );
    }

    return true;
  }

  // Validate category name format and length
  static validateNameFormat(name) {
    if (!name || typeof name !== 'string') {
      throw new Error('Category name is required and must be a string');
    }

    const trimmedName = name.trim();

    if (trimmedName.length === 0) {
      throw new Error('Category name cannot be empty');
    }

    if (trimmedName.length > 100) {
      throw new Error('Category name cannot exceed 100 characters');
    }

    // Check for invalid characters
    const invalidChars = /[<>'"&]/;
    if (invalidChars.test(trimmedName)) {
      throw new Error('Category name contains invalid characters');
    }

    return trimmedName;
  }

  // Validate description format and length
  static validateDescription(description) {
    if (description === null || description === undefined) {
      return null;
    }

    if (typeof description !== 'string') {
      throw new Error('Description must be a string');
    }

    const trimmedDescription = description.trim();

    if (trimmedDescription.length > 1000) {
      throw new Error('Description cannot exceed 1000 characters');
    }

    return trimmedDescription || null;
  }

  // Validate image URL format
  static validateImageUrl(imageUrl) {
    if (imageUrl === null || imageUrl === undefined) {
      return null;
    }

    if (typeof imageUrl !== 'string') {
      throw new Error('Image URL must be a string');
    }

    const trimmedUrl = imageUrl.trim();

    if (trimmedUrl.length === 0) {
      return null;
    }

    if (trimmedUrl.length > 500) {
      throw new Error('Image URL cannot exceed 500 characters');
    }

    // Basic URL validation
    try {
      new URL(trimmedUrl);
    } catch (error) {
      throw new Error('Invalid image URL format');
    }

    // Check for allowed protocols
    const allowedProtocols = ['http:', 'https:'];
    const url = new URL(trimmedUrl);
    if (!allowedProtocols.includes(url.protocol)) {
      throw new Error('Image URL must use HTTP or HTTPS protocol');
    }

    return trimmedUrl;
  }

  // Validate sort order
  static validateSortOrder(sortOrder) {
    if (sortOrder === null || sortOrder === undefined) {
      return 0; // Default sort order
    }

    if (typeof sortOrder !== 'number' || !Number.isInteger(sortOrder)) {
      throw new Error('Sort order must be an integer');
    }

    if (sortOrder < 0) {
      throw new Error('Sort order cannot be negative');
    }

    if (sortOrder > 9999) {
      throw new Error('Sort order cannot exceed 9999');
    }

    return sortOrder;
  }

  // Validate metadata object
  static validateMetadata(metadata) {
    if (metadata === null || metadata === undefined) {
      return null;
    }

    if (typeof metadata !== 'object' || Array.isArray(metadata)) {
      throw new Error('Metadata must be an object');
    }

    // Validate metadata size (JSON string should not exceed 10KB)
    const metadataString = JSON.stringify(metadata);
    if (metadataString.length > 10240) {
      throw new Error('Metadata size cannot exceed 10KB');
    }

    // Validate metadata keys and values
    for (const [key, value] of Object.entries(metadata)) {
      if (typeof key !== 'string' || key.length > 100) {
        throw new Error('Metadata keys must be strings with max 100 characters');
      }

      if (value !== null && typeof value !== 'string' && typeof value !== 'number' && typeof value !== 'boolean') {
        throw new Error('Metadata values must be string, number, boolean, or null');
      }

      if (typeof value === 'string' && value.length > 1000) {
        throw new Error('Metadata string values cannot exceed 1000 characters');
      }
    }

    return metadata;
  }

  // Validate parent category existence and hierarchy constraints
  static async validateParentCategory(parentId, categoryId = null) {
    if (parentId === null || parentId === undefined) {
      return null; // Root category is valid
    }

    if (typeof parentId !== 'number' || !Number.isInteger(parentId)) {
      throw new Error('Parent ID must be an integer');
    }

    if (parentId <= 0) {
      throw new Error('Parent ID must be a positive integer');
    }

    // Check if parent exists
    const parent = await Category.findByPk(parentId);
    if (!parent) {
      throw new Error('Parent category not found');
    }

    // Check if parent is active
    if (!parent.is_active) {
      throw new Error('Cannot assign inactive parent category');
    }

    // If this is an update, validate hierarchy constraints
    if (categoryId) {
      await HierarchyService.validateHierarchy(categoryId, parentId);
    } else {
      // For new categories, check depth limit
      const parentDepth = await HierarchyService.getCategoryDepth(parentId);
      if (parentDepth >= HierarchyService.MAX_DEPTH - 1) {
        throw new Error(`Maximum hierarchy depth of ${HierarchyService.MAX_DEPTH} exceeded`);
      }
    }

    return parentId;
  }

  // Validate category creation data
  static async validateCategoryCreation(data) {
    const validatedData = {};

    // Required fields
    validatedData.name = this.validateNameFormat(data.name);

    // Optional fields
    validatedData.description = this.validateDescription(data.description);
    validatedData.image_url = this.validateImageUrl(data.image_url);
    validatedData.sort_order = this.validateSortOrder(data.sort_order);
    validatedData.metadata = this.validateMetadata(data.metadata);

    // Parent validation
    validatedData.parent_id = await this.validateParentCategory(data.parent_id);

    // Name uniqueness within parent scope
    await this.validateNameUniqueness(validatedData.name, validatedData.parent_id);

    return validatedData;
  }

  // Validate category update data
  static async validateCategoryUpdate(categoryId, data) {
    const validatedData = {};

    // Get current category
    const currentCategory = await Category.findByPk(categoryId);
    if (!currentCategory) {
      throw new Error('Category not found');
    }

    // Validate provided fields only
    if (data.name !== undefined) {
      validatedData.name = this.validateNameFormat(data.name);

      // Check name uniqueness if name is changing
      if (validatedData.name !== currentCategory.name) {
        await this.validateNameUniqueness(
          validatedData.name,
          data.parent_id !== undefined ? data.parent_id : currentCategory.parent_id,
          categoryId
        );
      }
    }

    if (data.description !== undefined) {
      validatedData.description = this.validateDescription(data.description);
    }

    if (data.image_url !== undefined) {
      validatedData.image_url = this.validateImageUrl(data.image_url);
    }

    if (data.sort_order !== undefined) {
      validatedData.sort_order = this.validateSortOrder(data.sort_order);
    }

    if (data.metadata !== undefined) {
      validatedData.metadata = this.validateMetadata(data.metadata);
    }

    if (data.is_active !== undefined) {
      if (typeof data.is_active !== 'boolean') {
        throw new Error('is_active must be a boolean value');
      }

      // If deactivating, check for active children
      if (!data.is_active && currentCategory.is_active) {
        const hasActiveChildren = await currentCategory.hasActiveChildren();
        if (hasActiveChildren) {
          throw new Error('Cannot deactivate category with active children');
        }
      }

      validatedData.is_active = data.is_active;
    }

    // Parent validation (must be last to use updated name if provided)
    if (data.parent_id !== undefined) {
      validatedData.parent_id = await this.validateParentCategory(data.parent_id, categoryId);

      // If both name and parent are changing, recheck uniqueness
      if (data.name !== undefined) {
        await this.validateNameUniqueness(
          validatedData.name,
          validatedData.parent_id,
          categoryId
        );
      }
    }

    return validatedData;
  }

  // Validate category deletion constraints
  static async validateCategoryDeletion(categoryId, force = false) {
    const category = await Category.findByPk(categoryId);
    if (!category) {
      throw new Error('Category not found');
    }

    if (!force) {
      // Check for active children
      const hasActiveChildren = await category.hasActiveChildren();
      if (hasActiveChildren) {
        throw new Error('Cannot delete category with active children. Use force=true to deactivate instead.');
      }
    }

    return true;
  }

  // Validate search query
  static validateSearchQuery(query) {
    if (!query || typeof query !== 'string') {
      throw new Error('Search query is required and must be a string');
    }

    const trimmedQuery = query.trim();

    if (trimmedQuery.length === 0) {
      throw new Error('Search query cannot be empty');
    }

    if (trimmedQuery.length < 2) {
      throw new Error('Search query must be at least 2 characters long');
    }

    if (trimmedQuery.length > 100) {
      throw new Error('Search query cannot exceed 100 characters');
    }

    // Basic security check for SQL injection patterns
    const dangerousPatterns = /[';--\/\*\*\/xp_cmdshell]/i;
    if (dangerousPatterns.test(trimmedQuery)) {
      throw new Error('Search query contains invalid characters');
    }

    return trimmedQuery;
  }

  // Validate pagination parameters
  static validatePaginationParams(page, limit) {
    const validatedParams = {};

    // Validate page
    if (page !== undefined) {
      const pageNum = parseInt(page, 10);
      if (isNaN(pageNum) || pageNum < 1) {
        throw new Error('Page must be a positive integer');
      }
      if (pageNum > 1000) {
        throw new Error('Page number cannot exceed 1000');
      }
      validatedParams.page = pageNum;
    } else {
      validatedParams.page = 1;
    }

    // Validate limit
    if (limit !== undefined) {
      const limitNum = parseInt(limit, 10);
      if (isNaN(limitNum) || limitNum < 1) {
        throw new Error('Limit must be a positive integer');
      }
      if (limitNum > 100) {
        throw new Error('Limit cannot exceed 100');
      }
      validatedParams.limit = limitNum;
    } else {
      validatedParams.limit = 20;
    }

    return validatedParams;
  }

  // Comprehensive data validation for API requests
  static async validateRequest(operation, data, categoryId = null) {
    try {
      switch (operation) {
        case 'create':
          return await this.validateCategoryCreation(data);

        case 'update':
          return await this.validateCategoryUpdate(categoryId, data);

        case 'delete':
          await this.validateCategoryDeletion(categoryId, data.force);
          return true;

        case 'search':
          return {
            query: this.validateSearchQuery(data.query),
            active_only: data.active_only !== false
          };

        case 'pagination':
          return this.validatePaginationParams(data.page, data.limit);

        default:
          throw new Error(`Unknown validation operation: ${operation}`);
      }
    } catch (error) {
      // Add context to validation errors
      error.name = 'ValidationError';
      error.operation = operation;
      error.categoryId = categoryId;
      throw error;
    }
  }
}

module.exports = ValidationService;