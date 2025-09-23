"""Product service containing CRUD operations and business logic."""

import logging

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.models import CategoryEnum as ModelCategoryEnum
from src.models import Product
from src.schemas import ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)


class ProductService:
    """Service class for product operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_products(
        self,
        offset: int = 0,
        limit: int = 20,
        category: str | None = None,
        search_query: str | None = None,
        include_inactive: bool = False,
    ) -> tuple[list[Product], int]:
        """Get products with filtering and pagination.

        Args:
            offset: Number of products to skip
            limit: Maximum number of products to return
            category: Filter by category
            search_query: Search in name and description
            include_inactive: Whether to include inactive products

        Returns:
            Tuple of (products_list, total_count)

        """
        query = self.db.query(Product)

        # Filter by active status
        if not include_inactive:
            query = query.filter(Product.is_active == True)

        # Filter by category
        if category:
            try:
                category_enum = ModelCategoryEnum(category)
                query = query.filter(Product.category == category_enum)
            except ValueError:
                # Invalid category - return empty results
                return [], 0

        # Search functionality
        if search_query:
            search_term = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                ),
            )

        # Get total count before pagination
        total_count = query.count()

        # Apply pagination and ordering
        products = (
            query.order_by(Product.created_at.desc()).offset(offset).limit(limit).all()
        )

        return products, total_count

    def get_product_by_id(
        self, product_id: int, include_inactive: bool = True
    ) -> Product | None:
        """Get a product by its ID.

        Args:
            product_id: The product ID
            include_inactive: Whether to return inactive products

        Returns:
            Product if found, None otherwise

        """
        query = self.db.query(Product).filter(Product.id == product_id)

        if not include_inactive:
            query = query.filter(Product.is_active == True)

        return query.first()

    def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product.

        Args:
            product_data: Product creation data

        Returns:
            Created product

        Raises:
            ValueError: If product with same name already exists

        """
        # Check for duplicate name
        existing_product = (
            self.db.query(Product)
            .filter(Product.name == product_data.name.strip())
            .first()
        )

        if existing_product:
            raise ValueError(f"Product with name '{product_data.name}' already exists")

        # Convert schema enum to model enum
        category_enum = ModelCategoryEnum(product_data.category.value)

        # Create new product
        db_product = Product(
            name=product_data.name.strip(),
            description=product_data.description.strip(),
            price=product_data.price,
            category=category_enum,
            image_url=str(product_data.image_url),
            stock_quantity=product_data.stock_quantity,
            is_active=True,  # New products are active by default
        )

        try:
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            logger.info(f"Created product: {db_product.name} (ID: {db_product.id})")
            return db_product
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating product: {e}")
            raise

    def update_product(
        self, product_id: int, product_data: ProductUpdate
    ) -> Product | None:
        """Update an existing product.

        Args:
            product_id: The product ID to update
            product_data: Product update data

        Returns:
            Updated product if found, None otherwise

        Raises:
            ValueError: If update would create duplicate name

        """
        db_product = self.get_product_by_id(product_id)
        if not db_product:
            return None

        # Check for duplicate name if name is being updated
        if product_data.name is not None:
            name = product_data.name.strip()
            if name != db_product.name:
                existing_product = (
                    self.db.query(Product)
                    .filter(Product.name == name)
                    .filter(Product.id != product_id)
                    .first()
                )
                if existing_product:
                    raise ValueError(f"Product with name '{name}' already exists")

        # Update fields that are provided
        update_data = product_data.dict(exclude_unset=True)

        for field, value in update_data.items():
            if (field == "name" and value is not None) or (
                field == "description" and value is not None
            ):
                setattr(db_product, field, value.strip())
            elif field == "category" and value is not None:
                # Convert schema enum to model enum
                category_enum = ModelCategoryEnum(value.value)
                setattr(db_product, field, category_enum)
            elif field == "image_url" and value is not None:
                setattr(db_product, field, str(value))
            else:
                setattr(db_product, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_product)
            logger.info(f"Updated product: {db_product.name} (ID: {db_product.id})")
            return db_product
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating product {product_id}: {e}")
            raise

    def delete_product(self, product_id: int) -> bool:
        """Delete a product (soft delete by setting is_active=False).

        Args:
            product_id: The product ID to delete

        Returns:
            True if product was deleted, False if not found

        """
        db_product = self.get_product_by_id(product_id)
        if not db_product:
            return False

        db_product.is_active = False

        try:
            self.db.commit()
            logger.info(f"Deactivated product: {db_product.name} (ID: {db_product.id})")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating product {product_id}: {e}")
            raise

    def search_products(
        self,
        query: str,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Product], int]:
        """Search products by name and description.

        Args:
            query: Search query
            offset: Number of products to skip
            limit: Maximum number of products to return

        Returns:
            Tuple of (products_list, total_count)

        """
        if not query or not query.strip():
            return [], 0

        return self.get_products(
            offset=offset,
            limit=limit,
            search_query=query.strip(),
            include_inactive=False,
        )

    def get_products_by_category(
        self,
        category: str,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Product], int]:
        """Get products filtered by category.

        Args:
            category: Category to filter by
            offset: Number of products to skip
            limit: Maximum number of products to return

        Returns:
            Tuple of (products_list, total_count)

        """
        return self.get_products(
            offset=offset,
            limit=limit,
            category=category,
            include_inactive=False,
        )

    def get_product_count(self) -> int:
        """Get total number of active products."""
        return self.db.query(Product).filter(Product.is_active == True).count()

    def update_stock(self, product_id: int, new_stock: int) -> Product | None:
        """Update product stock quantity.

        Args:
            product_id: Product ID
            new_stock: New stock quantity

        Returns:
            Updated product if found, None otherwise

        """
        if new_stock < 0:
            raise ValueError("Stock quantity cannot be negative")

        db_product = self.get_product_by_id(product_id)
        if not db_product:
            return None

        db_product.stock_quantity = new_stock

        try:
            self.db.commit()
            self.db.refresh(db_product)
            logger.info(f"Updated stock for product {db_product.name}: {new_stock}")
            return db_product
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating stock for product {product_id}: {e}")
            raise
