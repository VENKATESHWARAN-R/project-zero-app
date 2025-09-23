"""
Token blacklist management utilities.
Implements in-memory token blacklisting from specification.
"""
import time
import logging
from typing import Dict, Set
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)


class InMemoryTokenBlacklist:
    """
    In-memory token blacklist for logout functionality.

    Tracks blacklisted JWT tokens by their JTI (JWT ID) until natural expiration.
    Thread-safe implementation for concurrent access.
    """

    def __init__(self):
        self._blacklisted_tokens: Dict[str, float] = {}  # jti -> expiration_timestamp
        self._lock = Lock()

    def blacklist_token(self, jti: str, expiration_timestamp: float):
        """
        Add a token to the blacklist.

        Args:
            jti (str): JWT ID (unique token identifier)
            expiration_timestamp (float): When token naturally expires
        """
        try:
            with self._lock:
                self._blacklisted_tokens[jti] = expiration_timestamp
                logger.info(f"Token {jti[:8]}... blacklisted until {datetime.fromtimestamp(expiration_timestamp)}")

        except Exception as e:
            logger.error(f"Error blacklisting token {jti}: {e}")

    def is_blacklisted(self, jti: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            jti (str): JWT ID to check

        Returns:
            bool: True if token is blacklisted, False otherwise
        """
        try:
            if not jti:
                return False

            with self._lock:
                # Check if token is in blacklist
                if jti not in self._blacklisted_tokens:
                    return False

                # Check if blacklist entry has expired
                expiration = self._blacklisted_tokens[jti]
                current_time = time.time()

                if current_time >= expiration:
                    # Token expiration reached, remove from blacklist
                    del self._blacklisted_tokens[jti]
                    return False

                return True

        except Exception as e:
            logger.error(f"Error checking blacklist for token {jti}: {e}")
            # On error, don't block the token (fail open)
            return False

    def cleanup_expired_tokens(self):
        """
        Remove expired tokens from blacklist.
        Should be called periodically to prevent memory leaks.
        """
        try:
            with self._lock:
                current_time = time.time()
                expired_tokens = []

                # Find expired tokens
                for jti, expiration in self._blacklisted_tokens.items():
                    if current_time >= expiration:
                        expired_tokens.append(jti)

                # Remove expired tokens
                for jti in expired_tokens:
                    del self._blacklisted_tokens[jti]

                if expired_tokens:
                    logger.info(f"Cleaned up {len(expired_tokens)} expired blacklisted tokens")

        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {e}")

    def get_blacklist_size(self) -> int:
        """
        Get current number of blacklisted tokens.

        Returns:
            int: Number of blacklisted tokens
        """
        try:
            with self._lock:
                return len(self._blacklisted_tokens)

        except Exception as e:
            logger.error(f"Error getting blacklist size: {e}")
            return 0

    def get_blacklist_info(self) -> Dict:
        """
        Get information about the blacklist.

        Returns:
            Dict: Blacklist statistics
        """
        try:
            with self._lock:
                current_time = time.time()
                total_tokens = len(self._blacklisted_tokens)
                expired_count = 0

                for expiration in self._blacklisted_tokens.values():
                    if current_time >= expiration:
                        expired_count += 1

                return {
                    "total_blacklisted": total_tokens,
                    "expired_tokens": expired_count,
                    "active_blacklisted": total_tokens - expired_count,
                    "last_cleanup": datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Error getting blacklist info: {e}")
            return {
                "total_blacklisted": 0,
                "expired_tokens": 0,
                "active_blacklisted": 0,
                "last_cleanup": None
            }

    def clear_all(self):
        """
        Clear all blacklisted tokens.
        Used for testing and emergency cleanup.
        """
        try:
            with self._lock:
                count = len(self._blacklisted_tokens)
                self._blacklisted_tokens.clear()
                logger.warning(f"Cleared {count} tokens from blacklist")

        except Exception as e:
            logger.error(f"Error clearing blacklist: {e}")


# Global blacklist instance
token_blacklist = InMemoryTokenBlacklist()


def blacklist_token(jti: str, expiration_timestamp: float):
    """
    Convenience function to blacklist a token.

    Args:
        jti (str): JWT ID
        expiration_timestamp (float): Token expiration time
    """
    token_blacklist.blacklist_token(jti, expiration_timestamp)


def is_token_blacklisted(jti: str) -> bool:
    """
    Convenience function to check if token is blacklisted.

    Args:
        jti (str): JWT ID

    Returns:
        bool: True if blacklisted
    """
    return token_blacklist.is_blacklisted(jti)


def blacklist_token_by_jwt(token: str):
    """
    Blacklist a token by extracting its JTI and expiration.

    Args:
        token (str): JWT token to blacklist
    """
    try:
        from src.utils.jwt_utils import get_token_jti, decode_token

        # Get JTI from token
        jti = get_token_jti(token)
        if not jti:
            logger.warning("Cannot blacklist token: no JTI found")
            return

        # Get expiration from token
        try:
            payload = decode_token(token)
            exp = payload.get("exp")
            if exp:
                blacklist_token(jti, exp)
            else:
                # If no expiration, blacklist for a reasonable time (7 days)
                import time
                exp = time.time() + (7 * 24 * 60 * 60)
                blacklist_token(jti, exp)

        except Exception:
            # If we can't decode the token, still try to blacklist the JTI
            # Use a reasonable expiration time
            import time
            exp = time.time() + (7 * 24 * 60 * 60)  # 7 days
            blacklist_token(jti, exp)

    except Exception as e:
        logger.error(f"Error blacklisting token: {e}")


def get_blacklist_stats() -> Dict:
    """
    Get blacklist statistics.

    Returns:
        Dict: Blacklist information
    """
    return token_blacklist.get_blacklist_info()


def cleanup_blacklist():
    """
    Clean up expired tokens from blacklist.
    """
    token_blacklist.cleanup_expired_tokens()