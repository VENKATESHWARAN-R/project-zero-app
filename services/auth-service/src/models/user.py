"""
User model for authentication service.
Implements the User entity from data-model.md.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from src.database import Base


class User(Base):
    """
    User model representing authenticated user accounts.

    From data-model.md:
    - Core Fields: id, email, password_hash
    - Security Fields: is_active, created_at, failed_login_attempts, locked_until
    """
    __tablename__ = "users"

    # Core Fields
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Security Fields
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"

    def is_locked(self) -> bool:
        """
        Check if user account is currently locked.

        Returns:
            bool: True if account is locked, False otherwise
        """
        if self.locked_until is None:
            return False

        return datetime.utcnow() < self.locked_until

    def reset_failed_attempts(self):
        """
        Reset failed login attempts counter.
        Called after successful login.
        """
        self.failed_login_attempts = 0
        self.locked_until = None

    def increment_failed_attempts(self):
        """
        Increment failed login attempts counter.
        Lock account if threshold is reached.

        From specification: 5 failed attempts = 15 minute lockout
        """
        self.failed_login_attempts += 1

        # Lock account after 5 failed attempts for 15 minutes
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)

    def to_dict(self) -> dict:
        """
        Convert user to dictionary for API responses.

        Returns:
            dict: User data (excluding password_hash)
        """
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "failed_login_attempts": self.failed_login_attempts,
            "locked_until": self.locked_until.isoformat() if self.locked_until else None
        }