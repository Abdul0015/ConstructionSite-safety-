import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class AdminNotification(Base):
    """
    Persisted alert notifications triggered for site administrators upon critical events,
    such as 3 consecutive delivery count mismatches at a single gate.
    """
    __tablename__ = "admin_notifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="high", nullable=False)
    gate_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("gates.id", ondelete="SET NULL"), nullable=True)
    delivery_log_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("delivery_logs.id", ondelete="SET NULL"), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
