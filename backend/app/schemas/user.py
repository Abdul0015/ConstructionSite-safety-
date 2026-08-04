import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.WORKER

    model_config = ConfigDict(extra='forbid')

class UserCreate(UserBase):
    password: str

    model_config = ConfigDict(extra='forbid')

class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra='forbid')
