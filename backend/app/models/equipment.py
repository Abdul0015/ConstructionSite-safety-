import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base

class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    equipment_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "excavator", "bulldozer", "crane", "truck", "cement_mixer"
    identifier: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Registration or tag number
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="unknown", nullable=False)  # "unknown", "active", "idle", "offline"
    idle_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    idle_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    last_detected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, **kwargs):
        if "name" not in kwargs or kwargs.get("name") is None:
            identifier = kwargs.get("identifier")
            eq_type = kwargs.get("equipment_type", "Equipment")
            kwargs["name"] = identifier or f"{eq_type.capitalize()}"
        if "location" not in kwargs or kwargs.get("location") is None:
            kwargs["location"] = kwargs.get("location_description") or "Main Site"
        if "idle_duration_minutes" not in kwargs or kwargs.get("idle_duration_minutes") is None:
            kwargs["idle_duration_minutes"] = kwargs.get("idle_minutes", 0)
        super().__init__(**kwargs)
