"""Integration tests for error handling scenarios."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestErrorHandlingScenarios:
    """Test comprehensive error handling across the API."""

    def test_invalid_product_id_scenarios(self):
        """Test various invalid product ID scenarios."""
        invalid_ids = [
            "999999",  # Non-existent ID
            "0",  # Zero ID
            "-1",  # Negative ID
            "abc",  # Non-numeric
            "1.5",  # Float
            "1e10",  # Scientific notation
            "null",  # String null
            "",  # Empty string
        ]

        for invalid_id in invalid_ids:
            response = client.get(f"/products/{invalid_id}")

            # Should be either 404 (not found) or 422 (validation error)
            assert response.status_code in [404, 422]

            data = response.json()
            assert "detail" in data
            assert isinstance(data["detail"], str)

    def test_pagination_parameter_validation(self):
        """Test pagination parameter validation errors."""
        # Test negative offset
        response = client.get("/products?offset=-1")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

        # Test limit too large
        response = client.get("/products?limit=101")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

        # Test invalid offset type
        response = client.get("/products?offset=invalid")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

        # Test invalid limit type
        response = client.get("/products?limit=abc")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

        # Test floating point values
        response = client.get("/products?offset=1.5")
        assert response.status_code == 422

        response = client.get("/products?limit=2.7")
        assert response.status_code == 422

    def test_category_validation_errors(self):
        """Test category parameter validation."""
        invalid_categories = [
            "invalid_category",
            "ELECTRONICS",  # Wrong case
            "electronics-new",  # With suffix
            "123",  # Numeric
            "",  # Empty
            "null",  # String null
            "electronics clothing",  # Multiple categories
        ]

        for category in invalid_categories:
            response = client.get(f"/products/category/{category}")
            assert response.status_code == 400

            data = response.json()
            assert "detail" in data
            assert isinstance(data["detail"], str)

    def test_search_query_validation(self):
        """Test search query validation errors."""
        # Missing query parameter
        response = client.get("/products/search")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

        # Empty query
        response = client.get("/products/search?q=")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

        # Query too long
        long_query = "x" * 101  # Exceeds 100 character limit
        response = client.get(f"/products/search?q={long_query}")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

        # Only whitespace
        response = client.get("/products/search?q=   ")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_product_creation_validation_errors(self):
        """Test product creation validation errors."""
        admin_headers = {"Authorization": "Bearer valid_token"}

        # Test missing required fields
        incomplete_data = {"name": "Test Product"}
        response = client.post("/products", json=incomplete_data, headers=admin_headers)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

        # Test invalid price values
        invalid_price_data = {
            "name": "Test Product",
            "description": "Test description",
            "price": -10.00,  # Negative price
            "category": "electronics",
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }
        response = client.post(
            "/products", json=invalid_price_data, headers=admin_headers
        )
        assert response.status_code == 422

        # Test invalid category
        invalid_category_data = invalid_price_data.copy()
        invalid_category_data["price"] = 29.99
        invalid_category_data["category"] = "invalid_category"
        response = client.post(
            "/products", json=invalid_category_data, headers=admin_headers
        )
        assert response.status_code == 422

        # Test invalid URL
        invalid_url_data = invalid_category_data.copy()
        invalid_url_data["category"] = "electronics"
        invalid_url_data["image_url"] = "not_a_url"
        response = client.post(
            "/products", json=invalid_url_data, headers=admin_headers
        )
        assert response.status_code == 422

        # Test negative stock
        negative_stock_data = invalid_url_data.copy()
        negative_stock_data["image_url"] = "https://example.com/test.jpg"
        negative_stock_data["stock_quantity"] = -5
        response = client.post(
            "/products", json=negative_stock_data, headers=admin_headers
        )
        assert response.status_code == 422

        # Test field length limits
        long_name_data = {
            "name": "x" * 256,  # Exceeds 255 character limit
            "description": "Test description",
            "price": 29.99,
            "category": "electronics",
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }
        response = client.post("/products", json=long_name_data, headers=admin_headers)
        assert response.status_code == 422

        # Test empty strings
        empty_name_data = {
            "name": "",
            "description": "Test description",
            "price": 29.99,
            "category": "electronics",
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }
        response = client.post("/products", json=empty_name_data, headers=admin_headers)
        assert response.status_code == 422

    def test_product_update_validation_errors(self):
        """Test product update validation errors."""
        admin_headers = {"Authorization": "Bearer valid_token"}

        # Test updating non-existent product
        update_data = {"name": "Updated Name"}
        response = client.put(
            "/products/99999", json=update_data, headers=admin_headers
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

        # Test invalid data in updates
        invalid_updates = [
            {"price": -10.00},
            {"category": "invalid_category"},
            {"image_url": "not_a_url"},
            {"stock_quantity": -5},
            {"name": ""},
            {"description": ""},
            {"name": "x" * 256},
            {"description": "x" * 5001},
        ]

        for invalid_update in invalid_updates:
            response = client.put(
                "/products/1", json=invalid_update, headers=admin_headers
            )
            assert response.status_code in [404, 422]  # 404 if product 1 doesn't exist

    def test_authentication_error_handling(self):
        """Test authentication-related error scenarios."""
        product_data = {
            "name": "Test Product",
            "description": "Test description",
            "price": 29.99,
            "category": "electronics",
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }

        # No authorization header
        response = client.post("/products", json=product_data)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

        # Invalid token format
        invalid_headers = {"Authorization": "InvalidFormat"}
        response = client.post("/products", json=product_data, headers=invalid_headers)
        assert response.status_code == 401

        # Invalid bearer token
        invalid_bearer_headers = {"Authorization": "Bearer invalid_token"}
        response = client.post(
            "/products", json=product_data, headers=invalid_bearer_headers
        )
        assert response.status_code == 401

        # Empty token
        empty_token_headers = {"Authorization": "Bearer "}
        response = client.post(
            "/products", json=product_data, headers=empty_token_headers
        )
        assert response.status_code == 401

    def test_malformed_json_handling(self):
        """Test handling of malformed JSON requests."""
        admin_headers = {"Authorization": "Bearer valid_token"}

        # Test with invalid JSON for creation
        response = client.post(
            "/products",
            data='{"invalid": json}',  # Malformed JSON
            headers={**admin_headers, "Content-Type": "application/json"},
        )
        assert response.status_code == 422

        # Test with invalid JSON for update
        response = client.put(
            "/products/1",
            data='{"invalid": json}',  # Malformed JSON
            headers={**admin_headers, "Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_http_method_not_allowed(self):
        """Test unsupported HTTP methods."""
        # Test unsupported methods on various endpoints
        endpoints_and_methods = [
            ("/products", "DELETE"),
            ("/products", "PATCH"),
            ("/products/1", "POST"),
            ("/products/1", "DELETE"),
            ("/products/category/electronics", "POST"),
            ("/products/category/electronics", "PUT"),
            ("/products/search", "POST"),
            ("/health", "POST"),
            ("/health/ready", "PUT"),
        ]

        for endpoint, method in endpoints_and_methods:
            if method == "DELETE":
                response = client.delete(endpoint)
            elif method == "PATCH":
                response = client.patch(endpoint)
            elif method == "POST":
                response = client.post(endpoint)
            elif method == "PUT":
                response = client.put(endpoint)

            assert response.status_code == 405  # Method Not Allowed

    def test_content_type_validation(self):
        """Test content type validation for endpoints that expect JSON."""
        admin_headers = {"Authorization": "Bearer valid_token"}

        # Test creating product with wrong content type
        response = client.post(
            "/products",
            data="name=test&price=10",  # Form data instead of JSON
            headers={
                **admin_headers,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        assert response.status_code == 422

        # Test updating product with wrong content type
        response = client.put(
            "/products/1",
            data="name=test",  # Form data instead of JSON
            headers={
                **admin_headers,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        assert response.status_code == 422

    def test_error_response_consistency(self):
        """Test that error responses follow consistent format."""
        # Test various error scenarios and verify response format
        error_scenarios = [
            ("/products/99999", 404),
            ("/products?offset=-1", 400),
            ("/products/category/invalid", 400),
            ("/products/search?q=", 400),
            ("/products/search", 422),
        ]

        for endpoint, expected_status in error_scenarios:
            response = client.get(endpoint)
            assert response.status_code == expected_status

            data = response.json()

            # All error responses should have 'detail' field
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0

            # Check content type
            assert response.headers["content-type"] == "application/json"

    def test_edge_case_url_encoding(self):
        """Test edge cases with URL encoding."""
        # Test special characters in search
        special_queries = [
            "%20",  # Space
            "%3C%3E",  # < >
            "%22",  # Quote
            "%27",  # Apostrophe
        ]

        for query in special_queries:
            response = client.get(f"/products/search?q={query}")
            # Should handle gracefully, either return results or validation error
            assert response.status_code in [200, 400, 422]

        # Test special characters in category
        response = client.get("/products/category/%20")  # Space as category
        assert response.status_code == 400

    def test_concurrent_request_handling(self):
        """Test handling of multiple concurrent requests."""
        import threading

        results = []

        def make_request():
            response = client.get("/products?limit=1")
            results.append(response.status_code)

        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5
