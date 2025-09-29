const { Model, DataTypes } = require('sequelize');
const slugify = require('slugify');

class Category extends Model {
  static init(sequelize) {
    super.init(
      {
        id: {
          type: DataTypes.INTEGER,
          primaryKey: true,
          autoIncrement: true,
        },
        name: {
          type: DataTypes.STRING(100),
          allowNull: false,
          validate: {
            len: [1, 100],
            notEmpty: true,
          },
        },
        slug: {
          type: DataTypes.STRING(120),
          allowNull: false,
          unique: true,
        },
        description: {
          type: DataTypes.TEXT,
          allowNull: true,
        },
        image_url: {
          type: DataTypes.STRING(500),
          allowNull: true,
          validate: {
            isUrl: true,
          },
        },
        parent_id: {
          type: DataTypes.INTEGER,
          allowNull: true,
          references: {
            model: 'categories',
            key: 'id',
          },
        },
        sort_order: {
          type: DataTypes.INTEGER,
          allowNull: false,
          defaultValue: 0,
          validate: {
            min: 0,
          },
        },
        is_active: {
          type: DataTypes.BOOLEAN,
          allowNull: false,
          defaultValue: true,
        },
        metadata: {
          type: DataTypes.JSON,
          allowNull: true,
        },
      },
      {
        sequelize,
        modelName: 'Category',
        tableName: 'categories',
        underscored: true,
        timestamps: true,
        createdAt: 'created_at',
        updatedAt: 'updated_at',
        hooks: {
          beforeCreate: async (category) => {
            if (!category.slug) {
              category.slug = await Category.generateUniqueSlug(category.name);
            }
          },
          beforeUpdate: async (category) => {
            if (category.changed('name') && !category.changed('slug')) {
              category.slug = await Category.generateUniqueSlug(category.name, category.id);
            }
          },
        },
      }
    );

    return Category;
  }

  static associate(models) {
    // Self-referencing associations
    Category.belongsTo(Category, {
      as: 'parent',
      foreignKey: 'parent_id',
    });

    Category.hasMany(Category, {
      as: 'children',
      foreignKey: 'parent_id',
    });
  }

  // Generate unique slug from name
  static async generateUniqueSlug(name, excludeId = null) {
    const baseSlug = slugify(name, {
      lower: true,
      strict: true,
    });

    let slug = baseSlug;
    let counter = 1;

    while (true) {
      const whereClause = { slug };
      if (excludeId) {
        whereClause.id = { [this.sequelize.Sequelize.Op.ne]: excludeId };
      }

      const existing = await Category.findOne({ where: whereClause });
      if (!existing) {
        break;
      }

      slug = `${baseSlug}-${counter}`;
      counter++;
    }

    return slug;
  }

  // Get all ancestors up to root
  async getAncestors() {
    const ancestors = [];
    let current = this;

    while (current.parent_id) {
      const parent = await Category.findByPk(current.parent_id);
      if (!parent) break;

      ancestors.unshift(parent);
      current = parent;
    }

    return ancestors;
  }

  // Get all descendants with depth limit
  async getDescendants(maxDepth = 5, currentDepth = 0) {
    if (currentDepth >= maxDepth) {
      return [];
    }

    const children = await Category.findAll({
      where: { parent_id: this.id, is_active: true },
      order: [['sort_order', 'ASC'], ['name', 'ASC']],
    });

    const descendants = [];
    for (const child of children) {
      descendants.push(child);
      const grandChildren = await child.getDescendants(maxDepth, currentDepth + 1);
      descendants.push(...grandChildren);
    }

    return descendants;
  }

  // Get category path string
  async getPath() {
    const ancestors = await this.getAncestors();
    const pathParts = ancestors.map((cat) => cat.name);
    pathParts.push(this.name);
    return pathParts.join(' > ');
  }

  // Get depth in hierarchy
  async getDepth() {
    const ancestors = await this.getAncestors();
    return ancestors.length;
  }

  // Validate hierarchy to prevent circular references
  async validateHierarchy(newParentId) {
    if (!newParentId) return true; // Root category is always valid

    if (newParentId === this.id) {
      throw new Error('Category cannot be its own parent');
    }

    // Check if newParentId is a descendant of this category
    const descendants = await this.getDescendants();
    const descendantIds = descendants.map((cat) => cat.id);

    if (descendantIds.includes(newParentId)) {
      throw new Error('Cannot create circular hierarchy');
    }

    // Check depth limit
    const newParent = await Category.findByPk(newParentId);
    if (!newParent) {
      throw new Error('Parent category not found');
    }

    const newParentDepth = await newParent.getDepth();
    if (newParentDepth >= 4) { // Max depth is 5 (0-4)
      throw new Error('Maximum hierarchy depth exceeded');
    }

    return true;
  }

  // Check if category has active children
  async hasActiveChildren() {
    const count = await Category.count({
      where: { parent_id: this.id, is_active: true },
    });
    return count > 0;
  }

  // Get next sort order for siblings
  static async getNextSortOrder(parentId) {
    const maxSortOrder = await Category.max('sort_order', {
      where: { parent_id: parentId },
    });
    return (maxSortOrder || 0) + 10; // Increment by 10 to allow reordering
  }
}

module.exports = Category;