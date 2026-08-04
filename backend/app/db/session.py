import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

default_db_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "site_intelligence.db")
sqlite_fallback_uri = f"sqlite:///{default_db_file}"

db_uri = os.getenv("SQLALCHEMY_DATABASE_URI", None)
if not db_uri:
    db_uri = sqlite_fallback_uri

try:
    if "sqlite" in db_uri:
        engine = create_engine(db_uri, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_uri, pool_pre_ping=True, pool_size=10, max_overflow=20)
except Exception:
    engine = create_engine(sqlite_fallback_uri, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency for yielding database sessions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
