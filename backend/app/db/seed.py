import logging
import json
from datetime import datetime
from decimal import Decimal
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.models import User, UserRole, Zone, Gate, Violation, HazardReport, DeliveryLog, Equipment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def seed_db():
    from app.db.base_class import Base
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        logger.info("Checking existing seed data...")
        if db.query(User).filter(User.email == "admin@siteintel.com").first():
            logger.info("Database already seeded. Skipping.")
            return

        logger.info("Seeding users...")
        admin = User(
            email="admin@siteintel.com",
            password_hash=hash_password("AdminSecurePass123!"),
            full_name="Rajesh Admin",
            role=UserRole.ADMIN
        )
        supervisor = User(
            email="supervisor@siteintel.com",
            password_hash=hash_password("SupervisorSecurePass123!"),
            full_name="Meena Supervisor",
            role=UserRole.SUPERVISOR
        )
        worker = User(
            email="worker@siteintel.com",
            password_hash=hash_password("WorkerSecurePass123!"),
            full_name="Arjun Worker",
            role=UserRole.WORKER
        )

        db.add_all([admin, supervisor, worker])
        db.commit()
        db.refresh(admin)
        db.refresh(supervisor)
        db.refresh(worker)

        logger.info("Seeding zones (PRD Schema: zone_type, polygon_coords, camera_id, ppe_requirements)...")
        zone = Zone(
            name="Hazardous Excavation Zone Alpha",
            zone_type="excavation",
            polygon_coords=json.dumps([{"x": 100, "y": 200}, {"x": 300, "y": 200}, {"x": 300, "y": 400}, {"x": 100, "y": 400}]),
            camera_id="cam_zone_01",
            ppe_requirements=json.dumps(["helmet", "harness"]),
            is_active=True,
            created_by=admin.id
        )
        db.add(zone)

        logger.info("Seeding gates...")
        gate = Gate(
            name="Main Entry Gate 1",
            camera_stream_url="rtsp://admin:pass@192.168.1.100:554/stream1",
            location="North Site Perimeter"
        )
        db.add(gate)
        db.commit()
        db.refresh(zone)
        db.refresh(gate)

        logger.info("Seeding equipment (PRD Schema: equipment_type, identifier, location_description, status, idle_minutes)...")
        excavator = Equipment(
            equipment_type="excavator",
            identifier="EXC-001",
            location_description="Sector 4 Heavy Machinery Area",
            status="active",
            idle_minutes=5,
            last_detected_at=datetime.utcnow()
        )
        db.add(excavator)

        logger.info("Seeding delivery logs (PRD Schema: clean + discrepancy examples)...")
        delivery_clean = DeliveryLog(
            gate_id=gate.id,
            reported_by=supervisor.id,
            ai_vehicle_count=2,
            manual_reported_count=2,
            material_type="cement",
            material_quantity=Decimal("100.00"),
            quantity_unit="bags",
            vehicle_type="mixer",
            discrepancy_flag=False,
            discrepancy_resolved=False
        )
        delivery_discrepancy = DeliveryLog(
            gate_id=gate.id,
            reported_by=supervisor.id,
            ai_vehicle_count=3,
            manual_reported_count=2,
            material_type="sand",
            material_quantity=Decimal("15.50"),
            quantity_unit="tons",
            vehicle_type="tipper",
            discrepancy_flag=True,
            discrepancy_resolved=False
        )
        db.add_all([delivery_clean, delivery_discrepancy])

        logger.info("Seeding safety violations (PRD Schema: status, acknowledged_by, acknowledged_at)...")
        violation = Violation(
            gate_id=gate.id,
            worker_id=worker.id,
            violation_type="ppe_missing",
            helmet_missing=True,
            vest_missing=False,
            image_url="/storage/violations/snapshot_001.jpg",
            status="pending"
        )
        db.add(violation)

        logger.info("Seeding hazard reports...")
        hazard = HazardReport(
            reported_by=worker.id,
            description="Exposed electrical wiring near temporary water pump.",
            image_url="/storage/hazards/hazard_001.jpg",
            location="Zone B West Excavation Trench",
            category="unsafe_wiring"
        )
        db.add(hazard)

        db.commit()
        logger.info("Database seeding completed successfully!")

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
