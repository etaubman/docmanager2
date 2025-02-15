import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import shutil
from app.main import app
from app.database import Base, get_db

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    db = next(override_get_db())
    yield db
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def test_uploads_dir():
    uploads_dir = "test_uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    yield uploads_dir
    shutil.rmtree(uploads_dir)