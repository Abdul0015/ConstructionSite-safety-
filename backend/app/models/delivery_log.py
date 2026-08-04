import uuid
from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, Numeric, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    gate_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("gates.id", ondelete="SET NULL"), nullable=True)
    reported_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    ai_vehicle_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=None)  # None = pending AI count, 0 = AI counted 0
    manual_reported_count: Mapped[int] = mapped_column(Integer, nullable=False)
    
    material_type: Mapped[str] = mapped_column(String(50), nullable=False)
    material_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity_unit: Mapped[str] = mapped_column(String(20), nullable=False)
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    discrepancy_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    discrepancy_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    gate: Mapped[Optional["Gate"]] = relationship("Gate", back_populates="delivery_logs")
    supervisor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reported_by], back_populates="delivery_logs")
    resolved_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[resolved_by])
