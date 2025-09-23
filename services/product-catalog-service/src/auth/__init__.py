"""Authentication package."""

from .dependencies import AdminRequired, verify_admin_token

__all__ = ["AdminRequired", "verify_admin_token"]
