from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
from app.models import BaseModel


# Create database engine
engine = create_engine(settings.database_url)

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
    """Create all database tables"""
    BaseModel.metadata.create_all(bind=engine)
    print("Database tables created successfully")

def drop_tables():
    """Drop all database tables"""
    BaseModel.metadata.drop_all(bind=engine)
    print("Database tables dropped")
