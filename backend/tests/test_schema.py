from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
from app.models import User, UserRole, Zone, Gate, Violation, HazardReport, DeliveryLog, Equipment

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_schema_creation_and_seed():
    # 1. Create all tables in memory SQLite database
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        # 2. Add test user
        user = User(
            email="testadmin@siteintel.com",
            password_hash="hashed_secret",
            full_name="Test Admin",
            role=UserRole.ADMIN
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.role == UserRole.ADMIN

        # 3. Add test gate & zone
        gate = Gate(name="Test Gate", location="North Perimeter")
        zone = Zone(name="Test Zone", polygon_coordinates="[]", site_location="Sector 1")
        db.add_all([gate, zone])
        db.commit()

        # 4. Add test delivery logs (v2 material tracking schema: clean + discrepancy)
        delivery_clean = DeliveryLog(
            gate_id=gate.id,
            reported_by=user.id,
            ai_vehicle_count=3,
            manual_reported_count=3,
            material_type="steel",
            material_quantity=25.5,
            quantity_unit="tons",
            vehicle_type="flatbed",
            discrepancy_flag=False
        )
        delivery_discrepancy = DeliveryLog(
            gate_id=gate.id,
            reported_by=user.id,
            ai_vehicle_count=4,
            manual_reported_count=2,
            material_type="sand",
            material_quantity=10.0,
            quantity_unit="tons",
            vehicle_type="tipper",
            discrepancy_flag=True
        )
        db.add_all([delivery_clean, delivery_discrepancy])
        db.commit()

        fetched_clean = db.query(DeliveryLog).filter(DeliveryLog.id == delivery_clean.id).first()
        assert fetched_clean is not None
        assert fetched_clean.discrepancy_flag is False

        fetched_discrepancy = db.query(DeliveryLog).filter(DeliveryLog.id == delivery_discrepancy.id).first()
        assert fetched_discrepancy is not None
        assert fetched_discrepancy.discrepancy_flag is True
        assert fetched_discrepancy.ai_vehicle_count != fetched_discrepancy.manual_reported_count
        print("SCHEMA & SEED TEST PASSED SUCCESSFULLY!")

    finally:
        db.close()

if __name__ == "__main__":
    test_schema_creation_and_seed()
