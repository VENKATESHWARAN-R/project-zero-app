from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ActivityResponse(BaseModel):
    id: int = Field(..., description="Activity log ID")
    user_id: int = Field(..., description="User ID")
    activity_type: str = Field(..., description="Type of activity")
    description: str = Field(..., description="Human-readable activity description")
    entity_type: Optional[str] = Field(None, description="Type of entity affected")
    entity_id: Optional[int] = Field(None, description="ID of entity affected")
    created_at: datetime = Field(..., description="Activity timestamp")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ActivityListResponse(BaseModel):
    activities: List[ActivityResponse] = Field(..., description="List of user activities")
    total: int = Field(..., description="Total number of activities for the user")
    limit: int = Field(..., description="Number of activities returned")
    offset: int = Field(..., description="Number of activities skipped")

    class Config:
        from_attributes = True