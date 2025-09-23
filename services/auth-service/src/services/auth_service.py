"""
User authentication service.
Handles user login, registration, and authentication logic.
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.user import User
from src.utils.password import hash_password, verify_password, validate_password_strength
from src.utils.jwt_utils import create_token_pair
from src.utils.rate_limiter import is_rate_limited, record_failed_login, record_successful_login

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Exception raised for authentication failures."""
    pass


class RateLimitError(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


class ValidationError(Exception):
    """Exception raised for validation failures."""
    pass


class AuthService:
    """Authentication service for user login and registration."""

    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, email: str, password: str, client_ip: str = None) -> Dict[str, Any]:
        """
        Authenticate a user with email and password.

        Args:
            email (str): User email
            password (str): User password
            client_ip (str): Client IP address for rate limiting

        Returns:
            Dict[str, Any]: Token response with access and refresh tokens

        Raises:
            RateLimitError: If rate limit is exceeded
            AuthenticationError: If authentication fails
            ValidationError: If input validation fails
        """
        try:
            # Input validation
            if not email or not password:
                raise ValidationError("Email and password are required")

            # Use email for rate limiting (could also use IP)
            rate_limit_key = email

            # Check rate limiting
            is_limited, locked_until = is_rate_limited(rate_limit_key)
            if is_limited:
                logger.warning(f"Rate limit exceeded for {email}")
                raise RateLimitError(f"Too many login attempts. Try again after {locked_until}")

            # Find user by email
            user = self.db.query(User).filter(User.email == email).first()

            if not user:
                # Record failed attempt even for non-existent users (prevent enumeration)
                record_failed_login(rate_limit_key)
                logger.info(f"Login attempt for non-existent user: {email}")
                raise AuthenticationError("Invalid email or password")

            # Check if user account is active
            if not user.is_active:
                record_failed_login(rate_limit_key)
                logger.warning(f"Login attempt for inactive user: {email}")
                raise AuthenticationError("Account is disabled")

            # Check if user account is locked
            if user.is_locked():
                record_failed_login(rate_limit_key)
                logger.warning(f"Login attempt for locked user: {email}")
                raise AuthenticationError("Account is temporarily locked")

            # Verify password
            if not verify_password(password, user.password_hash):
                # Record failed attempt
                record_failed_login(rate_limit_key)
                user.increment_failed_attempts()
                self.db.commit()

                logger.info(f"Failed login attempt for {email}")
                raise AuthenticationError("Invalid email or password")

            # Authentication successful
            record_successful_login(rate_limit_key)
            user.reset_failed_attempts()
            self.db.commit()

            # Create tokens
            tokens = create_token_pair(user.id)

            logger.info(f"Successful login for user {email}")
            return tokens

        except (RateLimitError, AuthenticationError, ValidationError):
            raise

        except Exception as e:
            logger.error(f"Error during authentication for {email}: {e}")
            raise AuthenticationError("Authentication failed")

    def register_user(self, email: str, password: str) -> User:
        """
        Register a new user.

        Args:
            email (str): User email
            password (str): User password

        Returns:
            User: Created user object

        Raises:
            ValidationError: If validation fails
            AuthenticationError: If user already exists
        """
        try:
            # Input validation
            if not email or not password:
                raise ValidationError("Email and password are required")

            # Validate email format (basic check)
            if "@" not in email or "." not in email.split("@")[1]:
                raise ValidationError("Invalid email format")

            # Validate password strength
            is_valid, errors = validate_password_strength(password)
            if not is_valid:
                raise ValidationError(f"Password validation failed: {', '.join(errors)}")

            # Check if user already exists
            existing_user = self.db.query(User).filter(User.email == email).first()
            if existing_user:
                logger.warning(f"Registration attempt for existing email: {email}")
                raise AuthenticationError("User already exists")

            # Hash password
            password_hash = hash_password(password)

            # Create user
            user = User(
                email=email,
                password_hash=password_hash,
                is_active=True
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            logger.info(f"New user registered: {email}")
            return user

        except (ValidationError, AuthenticationError):
            raise

        except IntegrityError:
            self.db.rollback()
            logger.warning(f"Registration failed - user already exists: {email}")
            raise AuthenticationError("User already exists")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during user registration for {email}: {e}")
            raise AuthenticationError("Registration failed")

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id (int): User ID

        Returns:
            Optional[User]: User object or None if not found
        """
        try:
            return self.db.query(User).filter(User.id == user_id).first()

        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email (str): User email

        Returns:
            Optional[User]: User object or None if not found
        """
        try:
            return self.db.query(User).filter(User.email == email).first()

        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None

    def update_user_password(self, user_id: int, new_password: str) -> bool:
        """
        Update user password.

        Args:
            user_id (int): User ID
            new_password (str): New password

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValidationError: If password validation fails
        """
        try:
            # Validate password strength
            is_valid, errors = validate_password_strength(new_password)
            if not is_valid:
                raise ValidationError(f"Password validation failed: {', '.join(errors)}")

            # Get user
            user = self.get_user_by_id(user_id)
            if not user:
                return False

            # Hash new password
            new_password_hash = hash_password(new_password)

            # Update password
            user.password_hash = new_password_hash
            user.reset_failed_attempts()  # Reset failed attempts on password change
            self.db.commit()

            logger.info(f"Password updated for user {user.email}")
            return True

        except ValidationError:
            raise

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating password for user {user_id}: {e}")
            return False

    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user account.

        Args:
            user_id (int): User ID

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False

            user.is_active = False
            self.db.commit()

            logger.info(f"User deactivated: {user.email}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating user {user_id}: {e}")
            return False

    def activate_user(self, user_id: int) -> bool:
        """
        Activate a user account.

        Args:
            user_id (int): User ID

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False

            user.is_active = True
            user.reset_failed_attempts()  # Reset failed attempts on activation
            self.db.commit()

            logger.info(f"User activated: {user.email}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error activating user {user_id}: {e}")
            return False