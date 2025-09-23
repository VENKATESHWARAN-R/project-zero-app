# Data Model: Product Catalog Service

**Date**: 2025-09-23
**Feature**: Product Catalog Service

## Entity Overview

The product catalog service manages two main entities: Products and Categories (embedded). The design prioritizes simplicity while supporting all required functionality for e-commerce product management.

## Product Entity

### Core Properties

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique product identifier |
| name | String(255) | Not Null, Unique | Product name for display and search |
| description | Text | Not Null | Detailed product description |
| price | Decimal(10,2) | Not Null, > 0 | Product price in currency units |
| category | String(50) | Not Null, Enum | Product category (electronics, clothing, books, home_goods) |
| image_url | String(500) | Not Null | URL to product image |
| stock_quantity | Integer | Not Null, >= 0 | Available inventory count |
| is_active | Boolean | Default True | Whether product is visible to customers |
| created_at | DateTime | Auto-generated | Record creation timestamp |
| updated_at | DateTime | Auto-updated | Record modification timestamp |

### Business Rules

1. **Name Uniqueness**: Product names must be unique across the catalog
2. **Price Validation**: Prices must be positive decimal values with 2 decimal places
3. **Category Constraint**: Categories limited to predefined enum values
4. **Stock Rules**: Stock quantity cannot be negative
5. **Active Status**: Only active products are visible in public endpoints
6. **URL Validation**: Image URLs must be valid HTTP/HTTPS URLs

### Category Values

The category field uses an enum with these predefined values:
- `electronics`: Consumer electronics, gadgets, devices
- `clothing`: Apparel, accessories, fashion items
- `books`: Physical and digital books, educational materials
- `home_goods`: Furniture, appliances, home decor

## Database Indexes

Strategic indexes to support common query patterns:

| Index Name | Columns | Purpose |
|------------|---------|---------|
| idx_product_category | category | Fast category filtering |
| idx_product_active | is_active | Efficient active product queries |
| idx_product_name_search | name (text search) | Product name search support |
| idx_product_created | created_at | Sorting by creation date |

## Data Validation Rules

### Input Validation (Pydantic Models)

**ProductCreate**:
- name: 1-255 characters, trimmed
- description: 1-5000 characters, trimmed
- price: Positive decimal, max 2 decimal places
- category: Valid enum value
- image_url: Valid URL format
- stock_quantity: Non-negative integer

**ProductUpdate**:
- All fields optional (partial updates)
- Same validation rules as create when provided
- Cannot update id, created_at

**ProductResponse**:
- All fields included for full representation
- Consistent formatting (price with 2 decimals)
- ISO datetime format for timestamps

## Relationships

### Current Design (Simple)
- Single table design (Product)
- Category as enum field (no separate table)
- No foreign key relationships

### Future Extensibility
The simple design can be extended without breaking changes:
- Add Category table with migration
- Add ProductImages table for multiple images
- Add ProductVariants for size/color options
- Add Reviews/Ratings relationship

## Sample Data Structure

### Sample Products by Category

**Electronics (6 products)**:
- Smartphone, Laptop, Headphones, Tablet, Smartwatch, Camera

**Clothing (6 products)**:
- T-Shirt, Jeans, Sneakers, Jacket, Dress, Hoodie

**Books (4 products)**:
- Programming Book, Fiction Novel, Science Textbook, Cookbook

**Home Goods (4 products)**:
- Coffee Table, Desk Lamp, Kitchen Set, Bedding Set

### Data Generation Strategy
- Realistic names and descriptions
- Price ranges appropriate for each category
- Stock quantities between 0-100
- Mix of active/inactive products for testing
- Valid image URLs (placeholder images)

## Query Patterns

### Common Query Operations

1. **List Active Products with Pagination**
   ```sql
   SELECT * FROM products
   WHERE is_active = true
   ORDER BY created_at DESC
   LIMIT ? OFFSET ?
   ```

2. **Filter by Category**
   ```sql
   SELECT * FROM products
   WHERE is_active = true AND category = ?
   ORDER BY created_at DESC
   ```

3. **Search Products**
   ```sql
   SELECT * FROM products
   WHERE is_active = true
   AND (name ILIKE ? OR description ILIKE ?)
   ORDER BY created_at DESC
   ```

4. **Get Product by ID**
   ```sql
   SELECT * FROM products WHERE id = ?
   ```

5. **Admin Operations** (include inactive products)
   ```sql
   SELECT * FROM products ORDER BY created_at DESC
   ```

### Performance Considerations

- Indexes support all common query patterns
- Category filtering uses indexed enum field
- Text search uses indexed name field (can be enhanced with full-text search)
- Pagination uses efficient LIMIT/OFFSET with indexed ordering

## Migration Strategy

### Initial Schema (V1)
- Create products table with all fields
- Add indexes for performance
- Insert sample data

### Future Migrations
- V2: Add full-text search indexes
- V3: Add category table if needed
- V4: Add product variants if needed

## Data Integrity

### Constraints
- Primary key ensures unique products
- Not null constraints on required fields
- Check constraint on price (must be positive)
- Check constraint on stock_quantity (non-negative)
- Enum constraint on category field

### Validation Layers
1. **Database Level**: SQL constraints and indexes
2. **ORM Level**: SQLAlchemy model validation
3. **API Level**: Pydantic model validation
4. **Business Logic**: Custom validation rules

This data model provides a solid foundation for the product catalog service while maintaining simplicity and allowing for future enhancements as requirements evolve.