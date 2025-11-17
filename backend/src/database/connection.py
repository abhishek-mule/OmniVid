from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# Database configuration
TESTING = os.getenv('TESTING', 'False').lower() in ('true', '1', 't')

if TESTING:
    # Use SQLite for testing
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATABASE_URL = f'sqlite:///{BASE_DIR}/test.db'
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # Use PostgreSQL for production/development
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://omnivid:password@localhost:5432/omnivid_db')
    engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)