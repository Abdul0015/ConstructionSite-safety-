import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class GateEntry(Base):
    """
    Audit log table recording every individual person detection/checkpoint entry at a gate.
    Stores pass/fail status for helmet and vest compliance.
    """
    __tablename__ = "gate_entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    gate_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("gates.id", ondelete="SET NULL"), nullable=True)
    person_track_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    passed_ppe: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    helmet_present: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    vest_present: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    gate: Mapped[Optional["Gate"]] = relationship("Gate", back_populates="gate_entries")
