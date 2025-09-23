"""Integration tests for admin product management scenarios."""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestAdminProductManagement:
    """Test complete admin product management workflows."""

    @pytest.fixture
    def admin_headers(self):
        """Mock admin authentication headers."""
        return {"Authorization": "Bearer valid_admin_token"}

    def test_create_new_product_workflow(self, admin_headers):
        """Test complete product creation workflow."""
        # Step 1: Create a new product
        new_product = {
            "name": "New Test Gadget",
            "description": "A revolutionary test gadget for integration testing",
            "price": 199.99,
            "category": "electronics",
            "image_url": "https://example.com/test-gadget.jpg",
            "stock_quantity": 25,
        }

        response = client.post("/products", json=new_product, headers=admin_headers)
        assert response.status_code == 201

        created_product = response.json()

        # Verify creation response
        assert created_product["name"] == new_product["name"]
        assert created_product["description"] == new_product["description"]
        assert created_product["price"] == new_product["price"]
        assert created_product["category"] == new_product["category"]
        assert created_product["image_url"] == new_product["image_url"]
        assert created_product["stock_quantity"] == new_product["stock_quantity"]
        assert created_product["is_active"] is True  # Default value
        assert "id" in created_product
        assert "created_at" in created_product
        assert "updated_at" in created_product

        product_id = created_product["id"]

        # Step 2: Verify product appears in public listings
        response = client.get("/products")
        assert response.status_code == 200

        all_products = response.json()["items"]
        created_product_in_list = next(
            (p for p in all_products if p["id"] == product_id),
            None,
        )
        assert created_product_in_list is not None
        assert created_product_in_list["name"] == new_product["name"]

        # Step 3: Verify product appears in category filtering
        response = client.get(f"/products/category/{new_product['category']}")
        assert response.status_code == 200

        category_products = response.json()["items"]
        created_product_in_category = next(
            (p for p in category_products if p["id"] == product_id),
            None,
        )
        assert created_product_in_category is not None

        # Step 4: Verify product is searchable
        response = client.get(f"/products/search?q={new_product['name'].split()[0]}")
        assert response.status_code == 200

        search_results = response.json()["items"]
        found_in_search = any(p["id"] == product_id for p in search_results)
        assert found_in_search

    def test_update_product_workflow(self, admin_headers):
        """Test complete product update workflow."""
        # First, get an existing product to update
        response = client.get("/products?limit=1")
        assert response.status_code == 200

        products = response.json()["items"]
        if not products:
            pytest.skip("No products available for update testing")

        original_product = products[0]
        product_id = original_product["id"]

        # Step 1: Update product information
        update_data = {
            "name": "Updated Product Name",
            "price": original_product["price"] + 10.00,
            "stock_quantity": original_product["stock_quantity"] + 5,
        }

        response = client.put(
            f"/products/{product_id}",
            json=update_data,
            headers=admin_headers,
        )
        assert response.status_code == 200

        updated_product = response.json()

        # Verify updates applied
        assert updated_product["name"] == update_data["name"]
        assert updated_product["price"] == update_data["price"]
        assert updated_product["stock_quantity"] == update_data["stock_quantity"]

        # Verify unchanged fields
        assert updated_product["id"] == product_id
        assert updated_product["description"] == original_product["description"]
        assert updated_product["category"] == original_product["category"]
        assert updated_product["created_at"] == original_product["created_at"]

        # Step 2: Verify changes are reflected in public view
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200

        public_view = response.json()
        assert public_view["name"] == update_data["name"]
        assert public_view["price"] == update_data["price"]

        # Step 3: Verify changes appear in listings
        response = client.get("/products")
        assert response.status_code == 200

        all_products = response.json()["items"]
        updated_in_list = next((p for p in all_products if p["id"] == product_id), None)
        assert updated_in_list is not None
        assert updated_in_list["name"] == update_data["name"]

    def test_deactivate_product_workflow(self, admin_headers):
        """Test deactivating a product."""
        # Get an active product
        response = client.get("/products?limit=1")
        assert response.status_code == 200

        products = response.json()["items"]
        if not products:
            pytest.skip("No products available for deactivation testing")

        active_product = products[0]
        product_id = active_product["id"]

        # Verify product is initially active
        assert active_product["is_active"] is True

        # Step 1: Deactivate the product
        response = client.put(
            f"/products/{product_id}",
            json={"is_active": False},
            headers=admin_headers,
        )
        assert response.status_code == 200

        deactivated_product = response.json()
        assert deactivated_product["is_active"] is False

        # Step 2: Verify product no longer appears in public listings
        response = client.get("/products")
        assert response.status_code == 200

        public_products = response.json()["items"]
        deactivated_in_public = any(p["id"] == product_id for p in public_products)
        assert not deactivated_in_public  # Should not appear

        # Step 3: Verify product doesn't appear in category filtering
        response = client.get(f"/products/category/{active_product['category']}")
        assert response.status_code == 200

        category_products = response.json()["items"]
        deactivated_in_category = any(p["id"] == product_id for p in category_products)
        assert not deactivated_in_category  # Should not appear

        # Step 4: Verify product doesn't appear in search
        response = client.get(f"/products/search?q={active_product['name']}")
        assert response.status_code == 200

        search_results = response.json()["items"]
        deactivated_in_search = any(p["id"] == product_id for p in search_results)
        assert not deactivated_in_search  # Should not appear

        # Step 5: But product should still be accessible directly
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200

        direct_access = response.json()
        assert direct_access["is_active"] is False

    def test_stock_management_workflow(self, admin_headers):
        """Test updating product stock levels."""
        # Get a product with stock
        response = client.get("/products?limit=5")
        assert response.status_code == 200

        products = response.json()["items"]
        product_with_stock = next(
            (p for p in products if p["stock_quantity"] > 0),
            None,
        )

        if not product_with_stock:
            pytest.skip("No products with stock available for testing")

        product_id = product_with_stock["id"]
        original_stock = product_with_stock["stock_quantity"]

        # Step 1: Reduce stock (simulate sales)
        new_stock = max(0, original_stock - 5)
        response = client.put(
            f"/products/{product_id}",
            json={"stock_quantity": new_stock},
            headers=admin_headers,
        )
        assert response.status_code == 200

        updated_product = response.json()
        assert updated_product["stock_quantity"] == new_stock

        # Step 2: Increase stock (simulate restocking)
        restocked_amount = new_stock + 10
        response = client.put(
            f"/products/{product_id}",
            json={"stock_quantity": restocked_amount},
            headers=admin_headers,
        )
        assert response.status_code == 200

        restocked_product = response.json()
        assert restocked_product["stock_quantity"] == restocked_amount

        # Step 3: Verify stock is visible in public view
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200

        public_view = response.json()
        assert public_view["stock_quantity"] == restocked_amount

    def test_authentication_required_workflow(self):
        """Test that admin operations require authentication."""
        # Prepare test data
        product_data = {
            "name": "Unauthorized Product",
            "description": "Should not be created",
            "price": 99.99,
            "category": "electronics",
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }

        # Step 1: Try to create product without auth
        response = client.post("/products", json=product_data)
        assert response.status_code == 401

        # Step 2: Try to create with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/products", json=product_data, headers=invalid_headers)
        assert response.status_code == 401

        # Step 3: Try to update without auth
        response = client.put("/products/1", json={"name": "Hacked Name"})
        assert response.status_code == 401

        # Step 4: Try to update with invalid token
        response = client.put(
            "/products/1",
            json={"name": "Hacked Name"},
            headers=invalid_headers,
        )
        assert response.status_code == 401

    def test_price_update_workflow(self, admin_headers):
        """Test updating product prices."""
        # Get a product to update
        response = client.get("/products?limit=1")
        assert response.status_code == 200

        products = response.json()["items"]
        if not products:
            pytest.skip("No products available for price testing")

        product = products[0]
        product_id = product["id"]
        original_price = product["price"]

        # Step 1: Update to higher price
        new_price = original_price + 25.00
        response = client.put(
            f"/products/{product_id}",
            json={"price": new_price},
            headers=admin_headers,
        )
        assert response.status_code == 200

        updated_product = response.json()
        assert updated_product["price"] == new_price

        # Step 2: Update to sale price
        sale_price = original_price - 10.00
        if sale_price > 0:  # Ensure positive price
            response = client.put(
                f"/products/{product_id}",
                json={"price": sale_price},
                headers=admin_headers,
            )
            assert response.status_code == 200

            sale_product = response.json()
            assert sale_product["price"] == sale_price

        # Step 3: Verify price changes are visible publicly
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200

        public_view = response.json()
        if sale_price > 0:
            assert public_view["price"] == sale_price
        else:
            assert public_view["price"] == new_price

    def test_category_change_workflow(self, admin_headers):
        """Test changing product category."""
        # Get a product
        response = client.get("/products?limit=1")
        assert response.status_code == 200

        products = response.json()["items"]
        if not products:
            pytest.skip("No products available for category testing")

        product = products[0]
        product_id = product["id"]
        original_category = product["category"]

        # Choose a different category
        categories = ["electronics", "clothing", "books", "home_goods"]
        new_category = next(c for c in categories if c != original_category)

        # Step 1: Change category
        response = client.put(
            f"/products/{product_id}",
            json={"category": new_category},
            headers=admin_headers,
        )
        assert response.status_code == 200

        updated_product = response.json()
        assert updated_product["category"] == new_category

        # Step 2: Verify product appears in new category
        response = client.get(f"/products/category/{new_category}")
        assert response.status_code == 200

        new_category_products = response.json()["items"]
        found_in_new_category = any(
            p["id"] == product_id for p in new_category_products
        )
        assert found_in_new_category

        # Step 3: Verify product no longer in original category
        response = client.get(f"/products/category/{original_category}")
        assert response.status_code == 200

        original_category_products = response.json()["items"]
        # Verify the product is no longer in the original category
        assert not any(
            p["id"] == product_id for p in original_category_products
        )
