"""Product API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.auth import AdminRequired
from src.database import get_db
from src.schemas import (
    CategoryEnum,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from src.services import ProductService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List products with pagination",
    description="Retrieve paginated list of active products",
)
async def list_products(
    offset: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(
        20, ge=1, le=100, description="Maximum number of products to return"
    ),
    db: Session = Depends(get_db),
):
    """List products with pagination."""
    try:
        service = ProductService(db)
        products, total = service.get_products(offset=offset, limit=limit)

        # Convert to response schema
        product_items = [
            ProductResponse.model_validate(product) for product in products
        ]

        return ProductListResponse(
            items=product_items,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + limit) < total,
        )

    except Exception as e:
        logger.error(f"Error listing products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new product (Admin)",
    description="Create a new product in the catalog",
    dependencies=[AdminRequired],
)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = AdminRequired,
):
    """Create a new product (requires admin authentication)."""
    try:
        service = ProductService(db)
        product = service.create_product(product_data)

        return ProductResponse.model_validate(product)

    except ValueError as e:
        # Business logic errors (e.g., duplicate name)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/search",
    response_model=ProductListResponse,
    summary="Search products",
    description="Search products by name or description with pagination",
)
async def search_products(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    offset: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(
        20, ge=1, le=100, description="Maximum number of products to return"
    ),
    db: Session = Depends(get_db),
):
    """Search products by name or description."""
    # Validate query
    query = q.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty",
        )

    if len(query) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query too long (maximum 100 characters)",
        )

    try:
        service = ProductService(db)
        products, total = service.search_products(
            query=query,
            offset=offset,
            limit=limit,
        )

        # Convert to response schema
        product_items = [
            ProductResponse.model_validate(product) for product in products
        ]

        return ProductListResponse(
            items=product_items,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + limit) < total,
        )

    except Exception as e:
        logger.error(f"Error searching products with query '{query}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    description="Retrieve detailed information about a specific product",
)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Get a product by its ID."""
    if product_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Product ID must be a positive integer",
        )

    try:
        service = ProductService(db)
        product = service.get_product_by_id(product_id, include_inactive=True)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        return ProductResponse.model_validate(product)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product (Admin)",
    description="Update an existing product",
    dependencies=[AdminRequired],
)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = AdminRequired,
):
    """Update an existing product (requires admin authentication)."""
    if product_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Product ID must be a positive integer",
        )

    try:
        service = ProductService(db)
        product = service.update_product(product_id, product_data)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        return ProductResponse.model_validate(product)

    except ValueError as e:
        # Business logic errors (e.g., duplicate name)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/category/{category}",
    response_model=ProductListResponse,
    summary="Filter products by category",
    description="Retrieve products filtered by category with pagination",
)
async def get_products_by_category(
    category: CategoryEnum,
    offset: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(
        20, ge=1, le=100, description="Maximum number of products to return"
    ),
    db: Session = Depends(get_db),
):
    """Get products filtered by category."""
    try:
        service = ProductService(db)
        products, total = service.get_products_by_category(
            category=category.value,
            offset=offset,
            limit=limit,
        )

        # Convert to response schema
        product_items = [
            ProductResponse.model_validate(product) for product in products
        ]

        return ProductListResponse(
            items=product_items,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + limit) < total,
        )

    except Exception as e:
        logger.error(f"Error getting products by category {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Note: Exception handlers are defined in the main app
