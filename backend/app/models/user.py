import uuid
from datetime import datetime
import enum
from sqlalchemy import String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    WORKER = "worker"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, native_enum=False), nullable=False, default=UserRole.WORKER)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    violations: Mapped[list["Violation"]] = relationship("Violation", foreign_keys="[Violation.worker_id]", back_populates="worker")
    hazard_reports: Mapped[list["HazardReport"]] = relationship("HazardReport", back_populates="reporter")
    delivery_logs: Mapped[list["DeliveryLog"]] = relationship("DeliveryLog", foreign_keys="[DeliveryLog.reported_by]", back_populates="supervisor")
