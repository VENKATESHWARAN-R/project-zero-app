"""
Rate limiting utilities for login attempts.
Implements in-memory rate limiting from specification.
"""
import time
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Rate limiting configuration from specification
MAX_ATTEMPTS = 5              # Maximum failed attempts
WINDOW_MINUTES = 15           # Time window for attempts
LOCKOUT_MINUTES = 15          # Lockout duration after max attempts


@dataclass
class RateLimitRecord:
    """Rate limit tracking record."""
    attempts: int
    window_start: datetime
    locked_until: Optional[datetime] = None


class InMemoryRateLimiter:
    """
    In-memory rate limiter for login attempts.

    Tracks failed login attempts per email/IP address.
    Implements 5 attempts per 15 minutes with 15-minute lockout.
    """

    def __init__(self):
        self._records: Dict[str, RateLimitRecord] = {}

    def is_rate_limited(self, identifier: str) -> tuple[bool, Optional[datetime]]:
        """
        Check if identifier is currently rate limited.

        Args:
            identifier (str): Email or IP address to check

        Returns:
            tuple[bool, Optional[datetime]]: (is_limited, locked_until)
        """
        try:
            record = self._records.get(identifier)

            if not record:
                return False, None

            now = datetime.utcnow()

            # Check if lockout has expired
            if record.locked_until and now >= record.locked_until:
                # Lockout expired, reset record
                del self._records[identifier]
                return False, None

            # Check if currently locked
            if record.locked_until and now < record.locked_until:
                return True, record.locked_until

            # Check if window has expired
            window_end = record.window_start + timedelta(minutes=WINDOW_MINUTES)
            if now >= window_end:
                # Window expired, reset record
                del self._records[identifier]
                return False, None

            # Check if max attempts reached
            if record.attempts >= MAX_ATTEMPTS:
                # Should be locked (safety check)
                if not record.locked_until:
                    record.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
                return True, record.locked_until

            return False, None

        except Exception as e:
            logger.error(f"Error checking rate limit for {identifier}: {e}")
            # On error, don't rate limit (fail open)
            return False, None

    def record_failed_attempt(self, identifier: str) -> bool:
        """
        Record a failed login attempt.

        Args:
            identifier (str): Email or IP address

        Returns:
            bool: True if now rate limited, False otherwise
        """
        try:
            now = datetime.utcnow()
            record = self._records.get(identifier)

            if not record:
                # First failed attempt
                self._records[identifier] = RateLimitRecord(
                    attempts=1,
                    window_start=now
                )
                return False

            # Check if window has expired
            window_end = record.window_start + timedelta(minutes=WINDOW_MINUTES)
            if now >= window_end:
                # Window expired, start new window
                self._records[identifier] = RateLimitRecord(
                    attempts=1,
                    window_start=now
                )
                return False

            # Increment attempts within current window
            record.attempts += 1

            # Check if max attempts reached
            if record.attempts >= MAX_ATTEMPTS:
                # Lock the identifier
                record.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
                logger.warning(f"Rate limit triggered for {identifier}: {record.attempts} attempts")
                return True

            return False

        except Exception as e:
            logger.error(f"Error recording failed attempt for {identifier}: {e}")
            # On error, don't rate limit (fail open)
            return False

    def record_successful_attempt(self, identifier: str):
        """
        Record a successful login attempt (resets rate limiting).

        Args:
            identifier (str): Email or IP address
        """
        try:
            # Reset rate limiting on successful login
            if identifier in self._records:
                del self._records[identifier]
                logger.info(f"Rate limit reset for {identifier} after successful login")

        except Exception as e:
            logger.error(f"Error recording successful attempt for {identifier}: {e}")

    def get_remaining_attempts(self, identifier: str) -> int:
        """
        Get remaining attempts before rate limiting.

        Args:
            identifier (str): Email or IP address

        Returns:
            int: Number of attempts remaining
        """
        try:
            is_limited, _ = self.is_rate_limited(identifier)

            if is_limited:
                return 0

            record = self._records.get(identifier)

            if not record:
                return MAX_ATTEMPTS

            # Check if window has expired
            now = datetime.utcnow()
            window_end = record.window_start + timedelta(minutes=WINDOW_MINUTES)
            if now >= window_end:
                return MAX_ATTEMPTS

            return max(0, MAX_ATTEMPTS - record.attempts)

        except Exception as e:
            logger.error(f"Error getting remaining attempts for {identifier}: {e}")
            return MAX_ATTEMPTS

    def cleanup_expired_records(self):
        """
        Clean up expired rate limiting records.
        Should be called periodically to prevent memory leaks.
        """
        try:
            now = datetime.utcnow()
            expired_keys = []

            for identifier, record in self._records.items():
                # Check if lockout has expired
                if record.locked_until and now >= record.locked_until:
                    expired_keys.append(identifier)
                    continue

                # Check if window has expired (only if not locked)
                if not record.locked_until:
                    window_end = record.window_start + timedelta(minutes=WINDOW_MINUTES)
                    if now >= window_end:
                        expired_keys.append(identifier)

            # Remove expired records
            for key in expired_keys:
                del self._records[key]

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired rate limit records")

        except Exception as e:
            logger.error(f"Error cleaning up rate limit records: {e}")

    def get_status(self, identifier: str) -> Dict:
        """
        Get detailed rate limiting status for an identifier.

        Args:
            identifier (str): Email or IP address

        Returns:
            Dict: Status information
        """
        try:
            record = self._records.get(identifier)

            if not record:
                return {
                    "is_rate_limited": False,
                    "attempts": 0,
                    "max_attempts": MAX_ATTEMPTS,
                    "remaining_attempts": MAX_ATTEMPTS,
                    "window_start": None,
                    "locked_until": None
                }

            is_limited, locked_until = self.is_rate_limited(identifier)
            remaining = self.get_remaining_attempts(identifier)

            return {
                "is_rate_limited": is_limited,
                "attempts": record.attempts,
                "max_attempts": MAX_ATTEMPTS,
                "remaining_attempts": remaining,
                "window_start": record.window_start.isoformat(),
                "locked_until": locked_until.isoformat() if locked_until else None
            }

        except Exception as e:
            logger.error(f"Error getting status for {identifier}: {e}")
            return {
                "is_rate_limited": False,
                "attempts": 0,
                "max_attempts": MAX_ATTEMPTS,
                "remaining_attempts": MAX_ATTEMPTS,
                "window_start": None,
                "locked_until": None
            }


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


def is_rate_limited(identifier: str) -> tuple[bool, Optional[datetime]]:
    """
    Convenience function to check rate limiting.

    Args:
        identifier (str): Email or IP address

    Returns:
        tuple[bool, Optional[datetime]]: (is_limited, locked_until)
    """
    return rate_limiter.is_rate_limited(identifier)


def record_failed_login(identifier: str) -> bool:
    """
    Convenience function to record failed login.

    Args:
        identifier (str): Email or IP address

    Returns:
        bool: True if now rate limited
    """
    return rate_limiter.record_failed_attempt(identifier)


def record_successful_login(identifier: str):
    """
    Convenience function to record successful login.

    Args:
        identifier (str): Email or IP address
    """
    rate_limiter.record_successful_attempt(identifier)


def get_rate_limit_status(identifier: str) -> Dict:
    """
    Convenience function to get rate limit status.

    Args:
        identifier (str): Email or IP address

    Returns:
        Dict: Status information
    """
    return rate_limiter.get_status(identifier)