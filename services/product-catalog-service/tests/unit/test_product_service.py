"""Unit tests for ProductService."""

from decimal import Decimal
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from src.models import CategoryEnum as ModelCategoryEnum
from src.models import Product
from src.schemas import CategoryEnum as SchemaCategoryEnum
from src.schemas import ProductCreate, ProductUpdate
from src.services.product_service import ProductService


class TestProductService:
    """Test ProductService class methods."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_db):
        """ProductService instance with mocked database."""
        return ProductService(mock_db)

    @pytest.fixture
    def sample_product(self):
        """Sample product for testing."""
        return Product(
            id=1,
            name="Test Product",
            description="Test description",
            price=Decimal("29.99"),
            category=ModelCategoryEnum.ELECTRONICS,
            image_url="https://example.com/test.jpg",
            stock_quantity=10,
            is_active=True,
        )

    @pytest.fixture
    def sample_product_create(self):
        """Sample ProductCreate schema."""
        return ProductCreate(
            name="New Product",
            description="New product description",
            price=Decimal("39.99"),
            category=SchemaCategoryEnum.ELECTRONICS,
            image_url="https://example.com/new.jpg",
            stock_quantity=15,
        )

    def test_get_products_default_params(self, service, mock_db, sample_product):
        """Test get_products with default parameters."""
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_product]

        mock_db.query.return_value = mock_query

        products, total = service.get_products()

        assert len(products) == 1
        assert total == 1
        assert products[0] == sample_product
        mock_db.query.assert_called_once()

    def test_get_products_with_category_filter(self, service, mock_db, sample_product):
        """Test get_products with category filter."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_product]

        mock_db.query.return_value = mock_query

        products, total = service.get_products(category="electronics")

        assert len(products) == 1
        assert total == 1
        # Should call filter twice (is_active and category)
        assert mock_query.filter.call_count == 2

    def test_get_products_with_invalid_category(self, service, mock_db):
        """Test get_products with invalid category returns empty."""
        products, total = service.get_products(category="invalid_category")

        assert products == []
        assert total == 0

    def test_get_products_with_search_query(self, service, mock_db, sample_product):
        """Test get_products with search query."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_product]

        mock_db.query.return_value = mock_query

        products, total = service.get_products(search_query="test")

        assert len(products) == 1
        assert total == 1
        # Should call filter twice (is_active and search)
        assert mock_query.filter.call_count == 2

    def test_get_product_by_id_found(self, service, mock_db, sample_product):
        """Test get_product_by_id when product exists."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_product

        mock_db.query.return_value = mock_query

        result = service.get_product_by_id(1)

        assert result == sample_product
        mock_db.query.assert_called_once()

    def test_get_product_by_id_not_found(self, service, mock_db):
        """Test get_product_by_id when product doesn't exist."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        mock_db.query.return_value = mock_query

        result = service.get_product_by_id(999)

        assert result is None

    def test_create_product_success(self, service, mock_db, sample_product_create):
        """Test successful product creation."""
        # Mock existing product check (no duplicate)
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        mock_db.query.return_value = mock_query

        # Mock the created product
        created_product = Mock()
        created_product.name = sample_product_create.name
        created_product.id = 1

        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        # Mock the add method to set the created product
        def mock_add_side_effect(product):
            # Simulate database setting ID after add
            product.id = 1
            return product

        mock_db.add.side_effect = mock_add_side_effect

        service.create_product(sample_product_create)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_product_duplicate_name(
        self, service, mock_db, sample_product_create, sample_product
    ):
        """Test product creation with duplicate name."""
        # Mock existing product check (duplicate found)
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_product  # Duplicate found

        mock_db.query.return_value = mock_query

        with pytest.raises(ValueError, match="already exists"):
            service.create_product(sample_product_create)

        # Should not call add/commit if duplicate found
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()

    def test_update_product_success(self, service, mock_db, sample_product):
        """Test successful product update."""
        # Mock get_product_by_id to return existing product
        service.get_product_by_id = Mock(return_value=sample_product)

        # Mock duplicate name check (no conflict)
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        mock_db.query.return_value = mock_query

        update_data = ProductUpdate(name="Updated Name", price=Decimal("49.99"))

        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        result = service.update_product(1, update_data)

        assert result == sample_product
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_update_product_not_found(self, service, mock_db):
        """Test update_product when product doesn't exist."""
        service.get_product_by_id = Mock(return_value=None)

        update_data = ProductUpdate(name="Updated Name")

        result = service.update_product(999, update_data)

        assert result is None
        mock_db.commit.assert_not_called()

    def test_update_product_duplicate_name(self, service, mock_db, sample_product):
        """Test update_product with duplicate name conflict."""
        # Mock get_product_by_id to return existing product
        service.get_product_by_id = Mock(return_value=sample_product)

        # Mock duplicate name check (conflict found)
        conflicting_product = Mock()
        conflicting_product.id = 2  # Different ID

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = conflicting_product

        mock_db.query.return_value = mock_query

        update_data = ProductUpdate(name="Existing Name")

        with pytest.raises(ValueError, match="already exists"):
            service.update_product(1, update_data)

        mock_db.commit.assert_not_called()

    def test_delete_product_success(self, service, mock_db, sample_product):
        """Test successful product deletion (soft delete)."""
        service.get_product_by_id = Mock(return_value=sample_product)
        mock_db.commit = Mock()

        result = service.delete_product(1)

        assert result is True
        assert sample_product.is_active is False
        mock_db.commit.assert_called_once()

    def test_delete_product_not_found(self, service, mock_db):
        """Test delete_product when product doesn't exist."""
        service.get_product_by_id = Mock(return_value=None)

        result = service.delete_product(999)

        assert result is False
        mock_db.commit.assert_not_called()

    def test_search_products_empty_query(self, service):
        """Test search_products with empty query."""
        results = service.search_products("")
        assert results == ([], 0)

        results = service.search_products("   ")
        assert results == ([], 0)

    def test_search_products_valid_query(self, service, mock_db, sample_product):
        """Test search_products with valid query."""
        # Mock get_products method
        service.get_products = Mock(return_value=([sample_product], 1))

        products, total = service.search_products("test query")

        assert len(products) == 1
        assert total == 1
        service.get_products.assert_called_once_with(
            offset=0,
            limit=20,
            search_query="test query",
            include_inactive=False,
        )

    def test_get_products_by_category(self, service, mock_db, sample_product):
        """Test get_products_by_category."""
        # Mock get_products method
        service.get_products = Mock(return_value=([sample_product], 1))

        products, total = service.get_products_by_category("electronics")

        assert len(products) == 1
        assert total == 1
        service.get_products.assert_called_once_with(
            offset=0,
            limit=20,
            category="electronics",
            include_inactive=False,
        )

    def test_update_stock_success(self, service, mock_db, sample_product):
        """Test successful stock update."""
        service.get_product_by_id = Mock(return_value=sample_product)
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        result = service.update_stock(1, 25)

        assert result == sample_product
        assert sample_product.stock_quantity == 25
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_update_stock_negative_value(self, service, mock_db):
        """Test update_stock with negative value."""
        with pytest.raises(ValueError, match="cannot be negative"):
            service.update_stock(1, -5)

    def test_update_stock_product_not_found(self, service, mock_db):
        """Test update_stock when product doesn't exist."""
        service.get_product_by_id = Mock(return_value=None)

        result = service.update_stock(999, 10)

        assert result is None
        mock_db.commit.assert_not_called()

    def test_get_product_count(self, service, mock_db):
        """Test get_product_count."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 42

        mock_db.query.return_value = mock_query

        count = service.get_product_count()

        assert count == 42
        mock_db.query.assert_called_once()
        mock_query.filter.assert_called_once()  # Should filter by is_active
