import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    zone_type: Mapped[str] = mapped_column(String(50), default="excavation", nullable=False)  # "crane", "high_voltage", "excavation", "chemical_storage"
    polygon_coords: Mapped[str] = mapped_column(Text, nullable=False)  # JSON-encoded array of points e.g. [{"x":10,"y":20}, ...] or [[10,20], ...]
    polygon_coordinates: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="[]", server_default="[]")
    site_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default="Main Site", server_default="Main Site")
    camera_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ppe_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON-encoded PPE rules list
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    violations: Mapped[list["Violation"]] = relationship("Violation", back_populates="zone")

    def __init__(self, **kwargs):
        if "polygon_coordinates" in kwargs and "polygon_coords" not in kwargs:
            kwargs["polygon_coords"] = kwargs["polygon_coordinates"]
        elif "polygon_coords" in kwargs and "polygon_coordinates" not in kwargs:
            kwargs["polygon_coordinates"] = kwargs["polygon_coords"]
        super().__init__(**kwargs)
