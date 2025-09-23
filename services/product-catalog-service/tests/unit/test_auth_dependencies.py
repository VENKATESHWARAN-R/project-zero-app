"""Unit tests for authentication dependencies."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.auth.dependencies import verify_admin_token


class TestVerifyAdminToken:
    """Test verify_admin_token function."""

    @pytest.fixture
    def mock_credentials(self):
        """Mock HTTPAuthorizationCredentials."""
        return HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid_test_token",
        )

    @pytest.mark.asyncio
    async def test_valid_token_success(self, mock_credentials):
        """Test successful token verification."""
        # Mock successful auth service response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "email": "admin@example.com",
            "user_id": 1,
            "roles": ["admin"],
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await verify_admin_token(mock_credentials)

            assert result["email"] == "admin@example.com"
            assert result["user_id"] == 1
            assert result["roles"] == ["admin"]

    @pytest.mark.asyncio
    async def test_invalid_token_401(self, mock_credentials):
        """Test token verification with invalid token."""
        # Mock 401 auth service response
        mock_response = Mock()
        mock_response.status_code = 401

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            with pytest.raises(HTTPException) as exc_info:
                await verify_admin_token(mock_credentials)

            assert exc_info.value.status_code == 401
            assert "Invalid authentication token" in str(exc_info.value.detail)
            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    @pytest.mark.asyncio
    async def test_auth_service_error_response(self, mock_credentials):
        """Test token verification with auth service error."""
        # Mock 500 auth service response
        mock_response = Mock()
        mock_response.status_code = 500

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            with pytest.raises(HTTPException) as exc_info:
                await verify_admin_token(mock_credentials)

            assert exc_info.value.status_code == 401
            assert "Authentication service error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_auth_service_timeout(self, mock_credentials):
        """Test token verification with auth service timeout."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.TimeoutException("Request timeout"),
            )

            with pytest.raises(HTTPException) as exc_info:
                await verify_admin_token(mock_credentials)

            assert exc_info.value.status_code == 503
            assert "Authentication service unavailable" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_auth_service_connection_error(self, mock_credentials):
        """Test token verification with auth service connection error."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.RequestError("Connection failed"),
            )

            with pytest.raises(HTTPException) as exc_info:
                await verify_admin_token(mock_credentials)

            assert exc_info.value.status_code == 503
            assert "Authentication service unavailable" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_unexpected_error(self, mock_credentials):
        """Test token verification with unexpected error."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("Unexpected error"),
            )

            with pytest.raises(HTTPException) as exc_info:
                await verify_admin_token(mock_credentials)

            assert exc_info.value.status_code == 500
            assert "Internal server error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_correct_auth_service_call(self, mock_credentials):
        """Test that auth service is called with correct parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"email": "test@example.com"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get

            with patch("src.auth.dependencies.settings") as mock_settings:
                mock_settings.AUTH_SERVICE_URL = "http://test-auth:8001"

                await verify_admin_token(mock_credentials)

                # Verify the call was made with correct parameters
                mock_get.assert_called_once_with(
                    "http://test-auth:8001/auth/verify",
                    headers={"Authorization": "Bearer valid_test_token"},
                    timeout=10.0,
                )

    @pytest.mark.asyncio
    async def test_empty_token(self):
        """Test verification with empty token."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="",
        )

        mock_response = Mock()
        mock_response.status_code = 401

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            with pytest.raises(HTTPException) as exc_info:
                await verify_admin_token(credentials)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_malformed_auth_response(self, mock_credentials):
        """Test handling of malformed auth service response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            with pytest.raises(HTTPException) as exc_info:
                await verify_admin_token(mock_credentials)

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_successful_logging(self, mock_credentials):
        """Test that successful verification logs correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "email": "admin@example.com",
            "user_id": 1,
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            with patch("src.auth.dependencies.logger") as mock_logger:
                await verify_admin_token(mock_credentials)

                # Verify successful logging
                mock_logger.info.assert_called_once_with(
                    "Token verified for user: admin@example.com",
                )

    @pytest.mark.asyncio
    async def test_failed_token_logging(self, mock_credentials):
        """Test that failed verification logs correctly."""
        mock_response = Mock()
        mock_response.status_code = 401

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            with patch("src.auth.dependencies.logger") as mock_logger:
                with pytest.raises(HTTPException):
                    await verify_admin_token(mock_credentials)

                # Verify warning logging
                mock_logger.warning.assert_called_once_with("Invalid token provided")

    @pytest.mark.asyncio
    async def test_auth_service_error_logging(self, mock_credentials):
        """Test that auth service errors are logged correctly."""
        mock_response = Mock()
        mock_response.status_code = 500

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            with patch("src.auth.dependencies.logger") as mock_logger:
                with pytest.raises(HTTPException):
                    await verify_admin_token(mock_credentials)

                # Verify error logging
                mock_logger.error.assert_called_once_with("Auth service error: 500")

    @pytest.mark.asyncio
    async def test_timeout_logging(self, mock_credentials):
        """Test that timeout errors are logged correctly."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout"),
            )

            with patch("src.auth.dependencies.logger") as mock_logger:
                with pytest.raises(HTTPException):
                    await verify_admin_token(mock_credentials)

                # Verify timeout logging
                mock_logger.error.assert_called_once_with("Auth service timeout")

    @pytest.mark.asyncio
    async def test_connection_error_logging(self, mock_credentials):
        """Test that connection errors are logged correctly."""
        connection_error = httpx.RequestError("Connection failed")

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=connection_error,
            )

            with patch("src.auth.dependencies.logger") as mock_logger:
                with pytest.raises(HTTPException):
                    await verify_admin_token(mock_credentials)

                # Verify connection error logging
                mock_logger.error.assert_called_once()
                call_args = mock_logger.error.call_args[0][0]
                assert "Auth service connection error" in call_args
