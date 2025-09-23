"""
Password hashing utilities using bcrypt.
Implements password security requirements from research.md.
"""
import bcrypt
import logging

logger = logging.getLogger(__name__)

# Configuration from research.md: 12 salt rounds for 2025
BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with 12 salt rounds.

    Args:
        password (str): Plain text password to hash

    Returns:
        str: Hashed password

    Raises:
        ValueError: If password is empty or None
    """
    if not password:
        raise ValueError("Password cannot be empty")

    try:
        # Convert password to bytes
        password_bytes = password.encode('utf-8')

        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Return as string
        return hashed.decode('utf-8')

    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise ValueError("Failed to hash password")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        password (str): Plain text password to verify
        hashed_password (str): Previously hashed password to check against

    Returns:
        bool: True if password matches hash, False otherwise
    """
    if not password or not hashed_password:
        return False

    try:
        # Convert to bytes
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        # Verify password
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength according to requirements.

    From specification:
    - Minimum 8 characters
    - Mixed case letters
    - Numbers required

    Args:
        password (str): Password to validate

    Returns:
        tuple[bool, list[str]]: (is_valid, list_of_errors)
    """
    errors = []

    if not password:
        errors.append("Password is required")
        return False, errors

    # Minimum length check
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    # Check for lowercase letter
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")

    # Check for uppercase letter
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")

    # Check for digit
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")

    # Maximum length check (bcrypt limitation)
    if len(password.encode('utf-8')) > 72:
        errors.append("Password is too long (maximum 72 bytes)")

    is_valid = len(errors) == 0
    return is_valid, errors


def is_password_secure(password: str) -> bool:
    """
    Quick check if password meets security requirements.

    Args:
        password (str): Password to check

    Returns:
        bool: True if password is secure, False otherwise
    """
    is_valid, _ = validate_password_strength(password)
    return is_valid