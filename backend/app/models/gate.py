import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class Gate(Base):
    __tablename__ = "gates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    camera_stream_url: Mapped[str] = mapped_column(String(500), nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    violations: Mapped[list["Violation"]] = relationship("Violation", back_populates="gate")
    delivery_logs: Mapped[list["DeliveryLog"]] = relationship("DeliveryLog", back_populates="gate")
    gate_entries: Mapped[list["GateEntry"]] = relationship("GateEntry", back_populates="gate")
