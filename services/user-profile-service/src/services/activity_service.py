from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.activity_log import ActivityLog


class ActivityService:
    def __init__(self, db: Session):
        self.db = db

    def log_activity(
        self,
        user_id: int,
        activity_type: str,
        description: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> ActivityLog:
        """Log a user activity."""
        activity = ActivityLog(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
            old_values=old_values,
            new_values=new_values
        )

        self.db.add(activity)
        # Note: Don't commit here - let the calling service handle the transaction
        return activity

    def get_user_activities(
        self,
        user_id: int,
        activity_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[ActivityLog], int]:
        """Get user activities with pagination."""
        query = self.db.query(ActivityLog).filter(ActivityLog.user_id == user_id)

        if activity_type:
            query = query.filter(ActivityLog.activity_type == activity_type)

        # Get total count for pagination
        total = query.count()

        # Apply pagination and ordering
        activities = query.order_by(desc(ActivityLog.created_at)).offset(offset).limit(limit).all()

        return activities, total

    def get_activity_by_id(self, user_id: int, activity_id: int) -> Optional[ActivityLog]:
        """Get a specific activity by ID for a user."""
        return self.db.query(ActivityLog).filter(
            ActivityLog.id == activity_id,
            ActivityLog.user_id == user_id
        ).first()

    def get_recent_activities_by_type(self, user_id: int, activity_type: str, limit: int = 5) -> List[ActivityLog]:
        """Get recent activities of a specific type for a user."""
        return self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            ActivityLog.activity_type == activity_type
        ).order_by(desc(ActivityLog.created_at)).limit(limit).all()

    def get_activity_summary(self, user_id: int, days: int = 30) -> Dict[str, int]:
        """Get activity summary for the last N days."""
        from datetime import timedelta

        since_date = datetime.utcnow() - timedelta(days=days)

        activities = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            ActivityLog.created_at >= since_date
        ).all()

        summary = {}
        for activity in activities:
            activity_type = activity.activity_type
            summary[activity_type] = summary.get(activity_type, 0) + 1

        return summary

    def cleanup_old_activities(self, user_id: int, days_to_keep: int = 365) -> int:
        """Clean up old activity logs (for data retention policies)."""
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        deleted_count = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            ActivityLog.created_at < cutoff_date
        ).delete()

        return deleted_count