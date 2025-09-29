# Data Model: Category Management Service

**Feature**: Category Management Service
**Date**: 2025-09-29
**Phase**: 1 - Data Model Design

## Entity Definitions

### Category Entity

**Purpose**: Represents a product category with hierarchical relationships and metadata.

**Attributes**:
- `id` (Integer, Primary Key, Auto-increment): Unique identifier for the category
- `name` (String, Required, Max 100 chars): Human-readable category name
- `slug` (String, Unique, Max 120 chars): URL-friendly identifier, auto-generated from name
- `description` (Text, Optional): Detailed description of the category
- `image_url` (String, Optional, Max 500 chars): URL to category image/icon
- `parent_id` (Integer, Foreign Key, Optional): Reference to parent category (self-referencing)
- `sort_order` (Integer, Default 0): Display order within parent category
- `is_active` (Boolean, Default true): Whether category is visible/active
- `metadata` (JSON, Optional): Additional category metadata (SEO, display preferences)
- `created_at` (DateTime, Auto): Record creation timestamp
- `updated_at` (DateTime, Auto): Record last update timestamp

**Relationships**:
- `parent`: Belongs to Category (self-referencing, optional)
- `children`: Has many Categories (self-referencing)
- `products`: Virtual relationship through Product Catalog Service

**Validation Rules**:
- `name`: Required, 1-100 characters, must be unique within parent scope
- `slug`: Auto-generated from name, URL-safe characters only
- `parent_id`: Cannot reference self or create circular hierarchy
- `image_url`: Valid URL format if provided
- `sort_order`: Non-negative integer
- Maximum hierarchy depth: 5 levels

**Business Rules**:
- Cannot delete category with active children
- Cannot move category to create circular reference
- Slug automatically generated and maintained
- Sort order auto-assigned if not specified

### Category Hierarchy View

**Purpose**: Computed view for efficient hierarchy queries and navigation.

**Attributes**:
- `category_id` (Integer): Reference to category
- `ancestor_id` (Integer): Reference to ancestor category
- `depth` (Integer): Depth level from ancestor (0 = self)
- `path` (String): Full category path (e.g., "Electronics/Computers/Laptops")

**Usage**:
- Efficient hierarchy traversal
- Path-based category lookups
- Depth validation (max 5 levels)
- Breadcrumb generation

## Database Schema

### Categories Table

```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    parent_id INTEGER,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    UNIQUE(name, parent_id), -- Unique name within parent scope
    CHECK (parent_id != id)  -- Prevent self-reference
);
```

### Indexes

```sql
-- Performance indexes
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_active ON categories(is_active);
CREATE INDEX idx_categories_sort_order ON categories(parent_id, sort_order);
CREATE INDEX idx_categories_name ON categories(name);
```

### Category Hierarchy Materialized View

```sql
-- Recursive CTE for hierarchy paths (created as needed)
WITH RECURSIVE category_hierarchy AS (
  -- Base case: root categories
  SELECT
    id as category_id,
    id as ancestor_id,
    0 as depth,
    name as path
  FROM categories
  WHERE parent_id IS NULL AND is_active = true

  UNION ALL

  -- Recursive case: child categories
  SELECT
    c.id as category_id,
    ch.ancestor_id,
    ch.depth + 1 as depth,
    ch.path || '/' || c.name as path
  FROM categories c
  JOIN category_hierarchy ch ON c.parent_id = ch.category_id
  WHERE c.is_active = true AND ch.depth < 4 -- Max depth 5 (0-4)
)
```

## Data Access Patterns

### Common Queries

1. **Get Category by ID**
   ```sql
   SELECT * FROM categories WHERE id = ? AND is_active = true;
   ```

2. **Get Root Categories**
   ```sql
   SELECT * FROM categories
   WHERE parent_id IS NULL AND is_active = true
   ORDER BY sort_order, name;
   ```

3. **Get Direct Children**
   ```sql
   SELECT * FROM categories
   WHERE parent_id = ? AND is_active = true
   ORDER BY sort_order, name;
   ```

4. **Get Category Hierarchy Path**
   ```sql
   WITH RECURSIVE path AS (
     SELECT id, name, parent_id, name as full_path, 1 as level
     FROM categories WHERE id = ?
     UNION ALL
     SELECT c.id, c.name, c.parent_id,
            c.name || ' > ' || p.full_path, p.level + 1
     FROM categories c
     JOIN path p ON c.id = p.parent_id
   )
   SELECT full_path FROM path WHERE parent_id IS NULL;
   ```

5. **Get All Descendants**
   ```sql
   WITH RECURSIVE descendants AS (
     SELECT id, name, parent_id, 1 as level
     FROM categories WHERE parent_id = ?
     UNION ALL
     SELECT c.id, c.name, c.parent_id, d.level + 1
     FROM categories c
     JOIN descendants d ON c.parent_id = d.id
     WHERE d.level < 5
   )
   SELECT * FROM descendants;
   ```

### Performance Considerations

- **Read-Heavy Optimization**: Categories are read much more than written
- **Indexing Strategy**: Indexes on parent_id, slug, and name for common queries
- **Caching**: Category hierarchy suitable for in-memory caching
- **Denormalization**: Consider storing computed paths for faster breadcrumb queries

### Data Integrity Constraints

1. **Circular Reference Prevention**
   - Check constraint prevents self-reference
   - Application logic validates against circular hierarchies
   - Maximum depth validation prevents infinite nesting

2. **Consistency Rules**
   - Cannot delete category with active children (application enforced)
   - Slug uniqueness maintained automatically
   - Parent-child relationships maintained through foreign keys

3. **Soft Delete Strategy**
   - Use `is_active` flag instead of hard deletion
   - Preserve hierarchy integrity when categories removed
   - Allow reactivation of previously deleted categories

## Migration Strategy

### SQLite to PostgreSQL Migration

**Schema Differences**:
- PostgreSQL uses SERIAL instead of AUTOINCREMENT
- JSON column support in both databases
- Constraint syntax differences handled by Sequelize

**Migration Script**:
```javascript
// Sequelize migration for categories table
module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.createTable('categories', {
      id: {
        type: Sequelize.INTEGER,
        primaryKey: true,
        autoIncrement: true
      },
      name: {
        type: Sequelize.STRING(100),
        allowNull: false
      },
      slug: {
        type: Sequelize.STRING(120),
        allowNull: false,
        unique: true
      },
      description: {
        type: Sequelize.TEXT,
        allowNull: true
      },
      image_url: {
        type: Sequelize.STRING(500),
        allowNull: true
      },
      parent_id: {
        type: Sequelize.INTEGER,
        references: {
          model: 'categories',
          key: 'id'
        },
        onDelete: 'SET NULL',
        allowNull: true
      },
      sort_order: {
        type: Sequelize.INTEGER,
        defaultValue: 0
      },
      is_active: {
        type: Sequelize.BOOLEAN,
        defaultValue: true
      },
      metadata: {
        type: Sequelize.JSON,
        allowNull: true
      },
      created_at: {
        type: Sequelize.DATE,
        allowNull: false,
        defaultValue: Sequelize.fn('NOW')
      },
      updated_at: {
        type: Sequelize.DATE,
        allowNull: false,
        defaultValue: Sequelize.fn('NOW')
      }
    });

    // Add indexes
    await queryInterface.addIndex('categories', ['parent_id']);
    await queryInterface.addIndex('categories', ['slug']);
    await queryInterface.addIndex('categories', ['is_active']);
    await queryInterface.addIndex('categories', ['parent_id', 'sort_order']);

    // Add unique constraint for name within parent scope
    await queryInterface.addIndex('categories', ['name', 'parent_id'], {
      unique: true,
      name: 'categories_name_parent_unique'
    });
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.dropTable('categories');
  }
};
```

## Sequelize Model Definition

```javascript
const { Model, DataTypes } = require('sequelize');

class Category extends Model {
  static associate(models) {
    // Self-referencing associations
    Category.belongsTo(Category, {
      as: 'parent',
      foreignKey: 'parent_id'
    });

    Category.hasMany(Category, {
      as: 'children',
      foreignKey: 'parent_id'
    });
  }

  // Instance methods
  async getAncestors() {
    // Get all ancestors up to root
  }

  async getDescendants() {
    // Get all descendants with depth limit
  }

  async getPath() {
    // Get category path string
  }

  validateHierarchy(newParentId) {
    // Validate no circular references
  }
}

Category.init({
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  name: {
    type: DataTypes.STRING(100),
    allowNull: false,
    validate: {
      len: [1, 100],
      notEmpty: true
    }
  },
  slug: {
    type: DataTypes.STRING(120),
    allowNull: false,
    unique: true
  },
  description: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  image_url: {
    type: DataTypes.STRING(500),
    allowNull: true,
    validate: {
      isUrl: true
    }
  },
  parent_id: {
    type: DataTypes.INTEGER,
    allowNull: true,
    references: {
      model: 'categories',
      key: 'id'
    }
  },
  sort_order: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    validate: {
      min: 0
    }
  },
  is_active: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },
  metadata: {
    type: DataTypes.JSON,
    allowNull: true
  }
}, {
  sequelize,
  modelName: 'Category',
  tableName: 'categories',
  underscored: true,
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: 'updated_at'
});
```

This data model provides a solid foundation for hierarchical category management while maintaining simplicity and performance. The design supports all functional requirements while preventing common pitfalls like circular references and infinite recursion.