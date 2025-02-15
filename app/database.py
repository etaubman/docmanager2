"""
Path: app/database.py
Description: Database configuration and session management
Purpose: Provides database connection and session handling for the application
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.logging_config import get_logger

logger = get_logger(__name__)

SQLALCHEMY_DATABASE_URL = "sqlite:///./documents.db"

logger.info(f"Initializing database connection: {SQLALCHEMY_DATABASE_URL}")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Generator function to handle database sessions
    Yields a database session and ensures proper cleanup
    """
    db = SessionLocal()
    logger.debug("Creating new database session")
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        logger.debug("Closing database session")
        db.close()