import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class HazardReportCreate(BaseModel):
    description: str
    location: str
    category: Optional[str] = "other"

    model_config = ConfigDict(extra='forbid')

class HazardReportResponse(BaseModel):
    id: uuid.UUID
    reported_by: Optional[uuid.UUID] = None
    description: str
    image_url: Optional[str] = None
    location: str
    category: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra='forbid')
