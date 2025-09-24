# Products API Contract

**Base URL**: `http://localhost:8004`
**Service**: Product Catalog Service
**Version**: v1

## Endpoints

### GET /products
Retrieve list of products with optional filtering and pagination.

**Query Parameters**:
- `category`: Filter by category slug
- `search`: Search in product name and description
- `min_price`: Minimum price filter (in cents)
- `max_price`: Maximum price filter (in cents)
- `in_stock`: Filter by stock availability (true/false)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `sort`: Sort field (name, price, created_at)
- `order`: Sort order (asc, desc)

**Example Request**:
```
GET /products?category=electronics&search=laptop&in_stock=true&page=1&limit=20
```

**Response (200 OK)**:
```json
{
  "products": [
    {
      "id": "product-uuid-123",
      "name": "Gaming Laptop Pro",
      "description": "High-performance gaming laptop with RTX graphics",
      "price": 149999,
      "currency": "USD",
      "category": "electronics",
      "image_url": "https://example.com/images/laptop-pro.jpg",
      "in_stock": true,
      "stock_quantity": 15,
      "created_at": "2025-09-24T10:00:00Z",
      "updated_at": "2025-09-24T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  },
  "filters_applied": {
    "category": "electronics",
    "search": "laptop",
    "in_stock": true
  }
}
```

### GET /products/{id}
Retrieve detailed information for a specific product.

**Path Parameters**:
- `id`: Product UUID

**Response (200 OK)**:
```json
{
  "id": "product-uuid-123",
  "name": "Gaming Laptop Pro",
  "description": "High-performance gaming laptop with RTX 4080 graphics, 32GB RAM, 1TB SSD",
  "price": 149999,
  "currency": "USD",
  "category": "electronics",
  "image_url": "https://example.com/images/laptop-pro.jpg",
  "images": [
    "https://example.com/images/laptop-pro-1.jpg",
    "https://example.com/images/laptop-pro-2.jpg"
  ],
  "in_stock": true,
  "stock_quantity": 15,
  "specifications": {
    "cpu": "Intel Core i9-13900H",
    "gpu": "NVIDIA RTX 4080",
    "ram": "32GB DDR5",
    "storage": "1TB NVMe SSD"
  },
  "created_at": "2025-09-24T10:00:00Z",
  "updated_at": "2025-09-24T10:00:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Product not found

### GET /categories
Retrieve list of product categories.

**Response (200 OK)**:
```json
{
  "categories": [
    {
      "id": "category-uuid-1",
      "name": "Electronics",
      "slug": "electronics",
      "description": "Electronic devices and gadgets",
      "parent_id": null,
      "product_count": 25
    },
    {
      "id": "category-uuid-2",
      "name": "Laptops",
      "slug": "laptops",
      "description": "Portable computers",
      "parent_id": "category-uuid-1",
      "product_count": 8
    }
  ]
}
```

### GET /products/{id}/related
Get related products for a specific product.

**Path Parameters**:
- `id`: Product UUID

**Query Parameters**:
- `limit`: Number of related products (default: 4, max: 10)

**Response (200 OK)**:
```json
{
  "related_products": [
    {
      "id": "product-uuid-456",
      "name": "Wireless Gaming Mouse",
      "price": 7999,
      "currency": "USD",
      "image_url": "https://example.com/images/mouse.jpg",
      "in_stock": true
    }
  ]
}
```

## Product Search

### GET /products/search
Advanced product search with faceted filtering.

**Query Parameters**:
- `q`: Search query (required)
- `categories[]`: Multiple category filters
- `price_range`: Price range in format "min,max"
- `brands[]`: Multiple brand filters
- `in_stock`: Stock availability filter
- `sort`: Sort field
- `order`: Sort order
- `page`: Page number
- `limit`: Items per page

**Response (200 OK)**:
```json
{
  "products": [...],
  "facets": {
    "categories": [
      {
        "slug": "electronics",
        "name": "Electronics",
        "count": 15
      }
    ],
    "brands": [
      {
        "name": "Dell",
        "count": 5
      }
    ],
    "price_ranges": [
      {
        "min": 50000,
        "max": 100000,
        "count": 8
      }
    ]
  },
  "pagination": {...},
  "search_info": {
    "query": "laptop",
    "total_results": 25,
    "search_time": 0.045
  }
}
```

## Error Response Format
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

## Caching Headers
- Products list: `Cache-Control: public, max-age=300`
- Product details: `Cache-Control: public, max-age=600`
- Categories: `Cache-Control: public, max-age=3600`

## Performance Notes
- All product images should be optimized and served via CDN
- Search results are limited to 100 items per page
- Related products algorithm considers category and price range
- Faceted search results include count information for filtering UI