import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class Violation(Base):
    __tablename__ = "violations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    gate_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("gates.id", ondelete="SET NULL"), nullable=True)
    zone_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("zones.id", ondelete="SET NULL"), nullable=True)
    worker_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    violation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "ppe_missing", "restricted_zone_entry"
    helmet_missing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    vest_missing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # "pending", "acknowledged", "escalated"
    acknowledged_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    gate: Mapped[Optional["Gate"]] = relationship("Gate", back_populates="violations")
    zone: Mapped[Optional["Zone"]] = relationship("Zone", back_populates="violations")
    worker: Mapped[Optional["User"]] = relationship("User", foreign_keys=[worker_id], back_populates="violations")
    acknowledged_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[acknowledged_by])
