from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

# SQLite database configuration
SQLITE_DATABASE_URL = "sqlite:///../database/weekend-overtime.sqlite"

# Create engine with WAL mode for better concurrency
engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 20,
        "isolation_level": None,
    },
    pool_pre_ping=True,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_china_day():
    """Get current day in China timezone"""
    try:
        if ZoneInfo:
            return datetime.now(ZoneInfo("Asia/Shanghai")).day
        else:
            return (datetime.utcnow() + timedelta(hours=8)).day
    except Exception:
        return datetime.utcnow().day
