"""Contract tests for GET /products/category/{category} endpoint."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_filter_by_category_success():
    """Test successful filtering by valid category."""
    for category in ["electronics", "clothing", "books", "home_goods"]:
        response = client.get(f"/products/category/{category}")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure matches ProductListResponse
        assert "items" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data
        assert "has_more" in data

        # Verify types
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["offset"], int)
        assert isinstance(data["limit"], int)
        assert isinstance(data["has_more"], bool)

        # Verify pagination defaults
        assert data["offset"] == 0
        assert data["limit"] == 20

        # Verify all returned products have the correct category
        for product in data["items"]:
            assert product["category"] == category


def test_filter_by_category_with_pagination():
    """Test category filtering with custom pagination."""
    response = client.get("/products/category/electronics?offset=5&limit=3")

    assert response.status_code == 200
    data = response.json()

    assert data["offset"] == 5
    assert data["limit"] == 3

    # All products should be electronics
    for product in data["items"]:
        assert product["category"] == "electronics"


def test_filter_by_invalid_category():
    """Test filtering by invalid category values."""
    invalid_categories = [
        "invalid",
        "ELECTRONICS",  # Case sensitive
        "electronic",  # Singular
        "phones",  # Not in enum
        "123",  # Numeric
        "electronics-new",  # With suffix
    ]

    for category in invalid_categories:
        response = client.get(f"/products/category/{category}")
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data


def test_filter_by_category_empty_result():
    """Test filtering by valid category with no results."""
    # This test assumes some categories might be empty
    # The response should still be well-formed
    response = client.get("/products/category/books")

    assert response.status_code == 200
    data = response.json()

    # Even if empty, structure should be correct
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)
    assert data["total"] >= 0
    assert data["offset"] == 0
    assert data["limit"] == 20
    assert isinstance(data["has_more"], bool)


def test_filter_by_category_invalid_pagination():
    """Test category filtering with invalid pagination parameters."""
    # Negative offset
    response = client.get("/products/category/electronics?offset=-1")
    assert response.status_code == 400

    # Limit too large
    response = client.get("/products/category/electronics?limit=101")
    assert response.status_code == 400

    # Invalid types
    response = client.get("/products/category/electronics?offset=invalid")
    assert response.status_code == 422


def test_filter_by_category_product_structure():
    """Test that filtered products have correct structure."""
    response = client.get("/products/category/electronics?limit=1")

    assert response.status_code == 200
    data = response.json()

    if data["items"]:
        product = data["items"][0]

        # Required fields from contract
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
            assert field in product

        # Verify category is correct
        assert product["category"] == "electronics"

        # Verify types
        assert isinstance(product["id"], int)
        assert isinstance(product["name"], str)
        assert isinstance(product["description"], str)
        assert isinstance(product["price"], (int, float))
        assert isinstance(product["image_url"], str)
        assert isinstance(product["stock_quantity"], int)
        assert isinstance(product["is_active"], bool)


def test_filter_by_category_only_active():
    """Test that category filtering only returns active products."""
    response = client.get("/products/category/electronics")

    assert response.status_code == 200
    data = response.json()

    # All returned products should be active
    for product in data["items"]:
        assert product["is_active"] is True


def test_filter_by_category_url_encoding():
    """Test category filtering with URL encoding."""
    # Test that normal categories work with URL encoding
    import urllib.parse

    for category in ["electronics", "clothing", "books", "home_goods"]:
        encoded_category = urllib.parse.quote(category)
        response = client.get(f"/products/category/{encoded_category}")

        assert response.status_code == 200
        data = response.json()

        for product in data["items"]:
            assert product["category"] == category


def test_filter_by_category_pagination_consistency():
    """Test pagination consistency across category filtering."""
    # Get first page
    response1 = client.get("/products/category/electronics?limit=2")
    assert response1.status_code == 200
    data1 = response1.json()

    # Get second page
    response2 = client.get("/products/category/electronics?offset=2&limit=2")
    assert response2.status_code == 200
    data2 = response2.json()

    # Should have different items (assuming enough products exist)
    if len(data1["items"]) == 2 and len(data2["items"]) > 0:
        item1_ids = {item["id"] for item in data1["items"]}
        item2_ids = {item["id"] for item in data2["items"]}
        assert item1_ids.isdisjoint(item2_ids)  # No overlap

    # has_more should be consistent
    if data1["total"] > 2:
        assert data1["has_more"] is True
    if data1["total"] <= 4:
        assert data2["has_more"] is False
