"""Integration tests for customer browsing experience scenarios."""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestCustomerBrowsingExperience:
    """Test complete customer browsing workflows."""

    def test_browse_all_products_with_pagination(self):
        """Test browsing all products with pagination."""
        # Step 1: Browse all products with default pagination
        response = client.get("/products")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "has_more" in data

        total_products = data["total"]
        first_page_items = data["items"]

        # Verify pagination metadata
        assert data["offset"] == 0
        assert data["limit"] == 20
        assert len(first_page_items) <= 20

        # Step 2: Browse with custom pagination (smaller pages)
        response = client.get("/products?limit=10")
        assert response.status_code == 200

        data = response.json()
        assert data["limit"] == 10
        assert len(data["items"]) <= 10

        # Step 3: Navigate to second page
        if total_products > 10:
            response = client.get("/products?offset=10&limit=10")
            assert response.status_code == 200

            data = response.json()
            assert data["offset"] == 10
            second_page_items = data["items"]

            # Items should be different from first page
            first_page_ids = {item["id"] for item in first_page_items[:10]}
            second_page_ids = {item["id"] for item in second_page_items}
            assert first_page_ids.isdisjoint(second_page_ids)

    def test_filter_by_electronics_category(self):
        """Test filtering by electronics category."""
        response = client.get("/products/category/electronics")
        assert response.status_code == 200

        data = response.json()
        electronics_products = data["items"]

        # All products should be electronics
        for product in electronics_products:
            assert product["category"] == "electronics"
            assert product["is_active"] is True

        # Should have reasonable product structure
        if electronics_products:
            product = electronics_products[0]
            assert "name" in product
            assert "price" in product
            assert "description" in product
            assert product["price"] > 0

    def test_filter_by_all_categories(self):
        """Test filtering by each available category."""
        categories = ["electronics", "clothing", "books", "home_goods"]

        category_counts = {}

        for category in categories:
            response = client.get(f"/products/category/{category}")
            assert response.status_code == 200

            data = response.json()
            category_counts[category] = data["total"]

            # All products should match the category
            for product in data["items"]:
                assert product["category"] == category

        # Should have products in multiple categories (for realistic test)
        categories_with_products = sum(
            1 for count in category_counts.values() if count > 0
        )
        assert (
            categories_with_products >= 2
        )  # At least 2 categories should have products

    def test_search_for_laptops(self):
        """Test searching for laptop products."""
        response = client.get("/products/search?q=laptop")
        assert response.status_code == 200

        data = response.json()
        laptop_products = data["items"]

        # All results should contain "laptop" in name or description
        for product in laptop_products:
            text_content = (product["name"] + " " + product["description"]).lower()
            assert "laptop" in text_content

        # Should be active products only
        for product in laptop_products:
            assert product["is_active"] is True

    def test_search_case_insensitive(self):
        """Test that search is case insensitive."""
        # Search for same term in different cases
        queries = ["laptop", "LAPTOP", "Laptop"]
        results = []

        for query in queries:
            response = client.get(f"/products/search?q={query}")
            assert response.status_code == 200
            results.append(response.json())

        # Should return similar number of results
        result_counts = [len(data["items"]) for data in results]
        if result_counts[0] > 0:
            # All counts should be the same
            assert all(count == result_counts[0] for count in result_counts)

    def test_view_specific_product_details(self):
        """Test viewing details of specific products."""
        # First, get a list of products to get valid IDs
        response = client.get("/products?limit=5")
        assert response.status_code == 200

        products = response.json()["items"]
        if not products:
            pytest.skip("No products available for testing")

        # Test viewing details of first product
        product_id = products[0]["id"]
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200

        product_detail = response.json()

        # Should have complete product information
        required_fields = [
            "id",
            "name",
            "description",
            "price",
            "category",
            "image_url",
            "stock_quantity",
            "is_active",
            "created_at",
            "updated_at",
        ]

        for field in required_fields:
            assert field in product_detail

        # Verify it's the same product
        assert product_detail["id"] == product_id

    def test_product_availability_check(self):
        """Test checking product availability (stock)."""
        response = client.get("/products?limit=10")
        assert response.status_code == 200

        products = response.json()["items"]

        # Check stock information for each product
        for product in products:
            assert "stock_quantity" in product
            assert isinstance(product["stock_quantity"], int)
            assert product["stock_quantity"] >= 0

            # Active products should generally have stock > 0
            # (though this depends on business rules)
            if product["is_active"]:
                # Just verify the field exists and is valid
                assert "stock_quantity" in product

    def test_complete_browsing_workflow(self):
        """Test complete customer browsing workflow."""
        # Step 1: Start with browsing all products
        response = client.get("/products?limit=5")
        assert response.status_code == 200
        all_products = response.json()

        # Step 2: Filter by a specific category
        response = client.get("/products/category/electronics?limit=3")
        assert response.status_code == 200
        electronics_data = response.json()
        assert len(electronics_data["items"]) <= 3
        assert all(item["category"] == "electronics" for item in electronics_data["items"])

        # Step 3: Search for specific items
        response = client.get("/products/search?q=phone&limit=3")
        assert response.status_code == 200
        search_data = response.json()
        assert len(search_data["items"]) <= 3

        # Step 4: View details of specific product
        if all_products["items"]:
            product_id = all_products["items"][0]["id"]
            response = client.get(f"/products/{product_id}")
            assert response.status_code == 200
            product_details = response.json()

            # Product details should have same ID
            assert product_details["id"] == product_id

        # All operations should succeed
        assert True

    def test_pagination_navigation_workflow(self):
        """Test navigating through multiple pages."""
        # Get total count
        response = client.get("/products?limit=1")
        assert response.status_code == 200
        total_count = response.json()["total"]

        if total_count <= 1:
            pytest.skip("Need more products for pagination testing")

        # Navigate through first few pages
        page_size = 3
        pages_to_test = min(3, (total_count // page_size) + 1)

        seen_product_ids = set()

        for page in range(pages_to_test):
            offset = page * page_size
            response = client.get(f"/products?offset={offset}&limit={page_size}")
            assert response.status_code == 200

            data = response.json()
            assert data["offset"] == offset
            assert data["limit"] == page_size

            # Collect product IDs to ensure no duplicates
            for product in data["items"]:
                product_id = product["id"]
                assert product_id not in seen_product_ids  # No duplicates
                seen_product_ids.add(product_id)

        # Should have seen multiple unique products
        assert len(seen_product_ids) > 1
