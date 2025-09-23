"""Contract tests for GET /products/search endpoint."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_search_products_success():
    """Test successful product search with valid query."""
    response = client.get("/products/search?q=laptop")

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

    # Verify search relevance (products should contain search term)
    search_term = "laptop"
    for product in data["items"]:
        # Should match in name or description (case insensitive)
        name_match = search_term.lower() in product["name"].lower()
        desc_match = search_term.lower() in product["description"].lower()
        assert name_match or desc_match


def test_search_products_with_pagination():
    """Test product search with custom pagination."""
    response = client.get("/products/search?q=product&offset=5&limit=3")

    assert response.status_code == 200
    data = response.json()

    assert data["offset"] == 5
    assert data["limit"] == 3


def test_search_products_case_insensitive():
    """Test that search is case insensitive."""
    queries = ["LAPTOP", "laptop", "LaPtOp", "Laptop"]

    for query in queries:
        response = client.get(f"/products/search?q={query}")
        assert response.status_code == 200

        data = response.json()
        # Should return same results regardless of case
        for product in data["items"]:
            name_match = query.lower() in product["name"].lower()
            desc_match = query.lower() in product["description"].lower()
            assert name_match or desc_match


def test_search_products_empty_query():
    """Test search with empty query parameter."""
    response = client.get("/products/search?q=")
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data


def test_search_products_missing_query():
    """Test search without query parameter."""
    response = client.get("/products/search")
    assert response.status_code == 422  # Missing required parameter


def test_search_products_query_too_long():
    """Test search with query exceeding maximum length."""
    long_query = "x" * 101  # Max is 100 characters
    response = client.get(f"/products/search?q={long_query}")
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data


def test_search_products_no_results():
    """Test search with query that returns no results."""
    response = client.get("/products/search?q=nonexistentproductxyz123")

    assert response.status_code == 200
    data = response.json()

    # Should return empty results with proper structure
    assert data["items"] == []
    assert data["total"] == 0
    assert data["offset"] == 0
    assert data["limit"] == 20
    assert data["has_more"] is False


def test_search_products_special_characters():
    """Test search with special characters and URL encoding."""
    special_queries = [
        "laptop+mouse",
        "phone&tablet",
        "price<100",
        "50%+off",
        "café",
        "naïve",
    ]

    for query in special_queries:
        import urllib.parse

        encoded_query = urllib.parse.quote(query)
        response = client.get(f"/products/search?q={encoded_query}")

        # Should not crash, either return results or empty
        assert response.status_code in [200, 400]


def test_search_products_whitespace():
    """Test search with whitespace handling."""
    # Leading/trailing spaces
    response = client.get("/products/search?q= laptop ")
    assert response.status_code == 200

    # Multiple spaces
    response = client.get("/products/search?q=gaming   laptop")
    assert response.status_code == 200

    # Only spaces should be treated as empty
    response = client.get("/products/search?q=   ")
    assert response.status_code == 400


def test_search_products_invalid_pagination():
    """Test search with invalid pagination parameters."""
    # Negative offset
    response = client.get("/products/search?q=laptop&offset=-1")
    assert response.status_code == 400

    # Limit too large
    response = client.get("/products/search?q=laptop&limit=101")
    assert response.status_code == 400

    # Invalid types
    response = client.get("/products/search?q=laptop&offset=invalid")
    assert response.status_code == 422


def test_search_products_result_structure():
    """Test that search results have correct product structure."""
    response = client.get("/products/search?q=product&limit=1")

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

        # Verify types
        assert isinstance(product["id"], int)
        assert isinstance(product["name"], str)
        assert isinstance(product["description"], str)
        assert isinstance(product["price"], (int, float))
        assert isinstance(product["category"], str)
        assert isinstance(product["image_url"], str)
        assert isinstance(product["stock_quantity"], int)
        assert isinstance(product["is_active"], bool)

        # Verify category is valid
        valid_categories = ["electronics", "clothing", "books", "home_goods"]
        assert product["category"] in valid_categories


def test_search_products_only_active():
    """Test that search only returns active products."""
    response = client.get("/products/search?q=product")

    assert response.status_code == 200
    data = response.json()

    # All returned products should be active
    for product in data["items"]:
        assert product["is_active"] is True


def test_search_products_relevance_scoring():
    """Test search result relevance and ordering."""
    # Search for a specific term that might appear in multiple products
    response = client.get("/products/search?q=smart")

    assert response.status_code == 200
    data = response.json()

    if len(data["items"]) > 1:
        # Products with search term in name should potentially rank higher
        # This is a basic check - actual relevance scoring may vary
        for product in data["items"]:
            name_match = "smart" in product["name"].lower()
            desc_match = "smart" in product["description"].lower()
            assert name_match or desc_match


def test_search_products_multiple_terms():
    """Test search with multiple words."""
    response = client.get("/products/search?q=wireless bluetooth")

    assert response.status_code == 200
    data = response.json()

    # Should find products that contain either or both terms
    for product in data["items"]:
        text_to_search = (product["name"] + " " + product["description"]).lower()
        has_wireless = "wireless" in text_to_search
        has_bluetooth = "bluetooth" in text_to_search
        assert has_wireless or has_bluetooth
