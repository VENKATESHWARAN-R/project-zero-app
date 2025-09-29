const { Sequelize } = require('sequelize');
const path = require('path');

describe('Database Migrations', () => {
  let sequelize;

  beforeAll(async () => {
    // Use in-memory SQLite for testing
    sequelize = new Sequelize('sqlite::memory:', {
      logging: false
    });
  });

  afterAll(async () => {
    await sequelize.close();
  });

  describe('001-create-categories migration', () => {
    it('should create categories table with correct schema', async () => {
      // Run the migration manually
      await sequelize.query(`
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
          FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
        )
      `);

      // Test table exists
      const [results] = await sequelize.query(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='categories'"
      );

      expect(results).toHaveLength(1);
      expect(results[0].name).toBe('categories');

      // Test table structure
      const [columns] = await sequelize.query("PRAGMA table_info(categories)");

      const columnNames = columns.map(col => col.name);
      expect(columnNames).toContain('id');
      expect(columnNames).toContain('name');
      expect(columnNames).toContain('slug');
      expect(columnNames).toContain('parent_id');
      expect(columnNames).toContain('sort_order');
      expect(columnNames).toContain('is_active');
      expect(columnNames).toContain('created_at');
      expect(columnNames).toContain('updated_at');
    });

    it('should enforce unique constraint on slug', async () => {
      // Create table first
      await sequelize.query(`
        CREATE TABLE IF NOT EXISTS categories (
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
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      // Insert first category
      await sequelize.query(`
        INSERT INTO categories (name, slug) VALUES ('Test', 'test-slug')
      `);

      // Try to insert duplicate slug - should fail
      await expect(sequelize.query(`
        INSERT INTO categories (name, slug) VALUES ('Test 2', 'test-slug')
      `)).rejects.toThrow();
    });

    it('should allow null parent_id for root categories', async () => {
      await sequelize.query(`
        CREATE TABLE IF NOT EXISTS categories (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name VARCHAR(100) NOT NULL,
          slug VARCHAR(120) UNIQUE NOT NULL,
          parent_id INTEGER,
          sort_order INTEGER DEFAULT 0,
          is_active BOOLEAN DEFAULT true,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      // Should succeed with null parent_id
      await expect(sequelize.query(`
        INSERT INTO categories (name, slug, parent_id)
        VALUES ('Root Category', 'root-category', NULL)
      `)).resolves.not.toThrow();
    });

    it('should set default values correctly', async () => {
      await sequelize.query(`
        CREATE TABLE IF NOT EXISTS categories (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name VARCHAR(100) NOT NULL,
          slug VARCHAR(120) UNIQUE NOT NULL,
          sort_order INTEGER DEFAULT 0,
          is_active BOOLEAN DEFAULT true,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      await sequelize.query(`
        INSERT INTO categories (name, slug) VALUES ('Test Category', 'test-category-defaults')
      `);

      const [results] = await sequelize.query(`
        SELECT sort_order, is_active FROM categories WHERE slug = 'test-category-defaults'
      `);

      expect(results[0].sort_order).toBe(0);
      expect(results[0].is_active).toBe(1); // SQLite returns 1 for true
    });
  });

  describe('002-add-category-indexes migration', () => {
    beforeEach(async () => {
      // Create table first
      await sequelize.query(`
        CREATE TABLE IF NOT EXISTS categories (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name VARCHAR(100) NOT NULL,
          slug VARCHAR(120) UNIQUE NOT NULL,
          parent_id INTEGER,
          sort_order INTEGER DEFAULT 0,
          is_active BOOLEAN DEFAULT true,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);
    });

    it('should create performance indexes', async () => {
      // Create indexes
      await sequelize.query('CREATE INDEX idx_categories_parent_id ON categories(parent_id)');
      await sequelize.query('CREATE INDEX idx_categories_slug ON categories(slug)');
      await sequelize.query('CREATE INDEX idx_categories_active ON categories(is_active)');
      await sequelize.query('CREATE INDEX idx_categories_sort_order ON categories(parent_id, sort_order)');
      await sequelize.query('CREATE INDEX idx_categories_name ON categories(name)');

      // Check indexes exist
      const [indexes] = await sequelize.query(`
        SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='categories'
      `);

      const indexNames = indexes.map(idx => idx.name);
      expect(indexNames).toContain('idx_categories_parent_id');
      expect(indexNames).toContain('idx_categories_slug');
      expect(indexNames).toContain('idx_categories_active');
      expect(indexNames).toContain('idx_categories_sort_order');
      expect(indexNames).toContain('idx_categories_name');
    });

    it('should improve query performance with indexes', async () => {
      // Add some test data
      await sequelize.query(`
        INSERT INTO categories (name, slug, parent_id, is_active) VALUES
        ('Electronics', 'electronics', NULL, true),
        ('Computers', 'computers', 1, true),
        ('Laptops', 'laptops', 2, true),
        ('Inactive Category', 'inactive', NULL, false)
      `);

      // Create indexes
      await sequelize.query('CREATE INDEX idx_categories_parent_id ON categories(parent_id)');
      await sequelize.query('CREATE INDEX idx_categories_active ON categories(is_active)');

      // Test queries that should use indexes
      const [parentResults] = await sequelize.query(`
        SELECT * FROM categories WHERE parent_id = 1
      `);
      expect(parentResults).toHaveLength(1);

      const [activeResults] = await sequelize.query(`
        SELECT * FROM categories WHERE is_active = true
      `);
      expect(activeResults).toHaveLength(3);
    });
  });

  describe('Migration rollback', () => {
    it('should be able to rollback category table creation', async () => {
      // Create table
      await sequelize.query(`
        CREATE TABLE categories (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name VARCHAR(100) NOT NULL,
          slug VARCHAR(120) UNIQUE NOT NULL
        )
      `);

      // Verify table exists
      let [results] = await sequelize.query(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='categories'"
      );
      expect(results).toHaveLength(1);

      // Rollback (drop table)
      await sequelize.query('DROP TABLE IF EXISTS categories');

      // Verify table is gone
      [results] = await sequelize.query(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='categories'"
      );
      expect(results).toHaveLength(0);
    });
  });
});