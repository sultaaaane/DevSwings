import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.core.database import get_session
import fakeredis
from app.core.redis import get_redis

import os
import pytest

# ...existing code...
# Use in-memory SQLite for tests
DATABASE_URL = "sqlite:///:memory:"

os.environ["TESTING"] = "true"


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override():
        return session

    def get_redis_override():
        return fakeredis.FakeRedis(decode_responses=True)

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_redis] = get_redis_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
