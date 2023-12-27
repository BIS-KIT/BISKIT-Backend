import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy_utils import database_exists, create_database

from main import app
from core.config import settings
from database.session import Base, get_db
from models.base import ModelBase
from models import utility as utility_models


DATABASE_URL = f"postgresql+psycopg2://postgres:{settings.DB_ROOT_PASSWORD}@maindb:5432/{settings.TEST_DB}"

engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if not database_exists(engine.url):
    create_database(engine.url)

ModelBase.metadata.create_all(bind=engine)


@pytest.fixture(scope="class")
def session():
    ModelBase.metadata.drop_all(bind=engine)
    ModelBase.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="class")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    # app에서 사용하는 DB를 오버라이드하는 부분
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="function")
def test_university(session):
    university = utility_models.University(kr_name="서울대학교 ")
    session.add(university)
    session.commit()

    return university


@pytest.fixture(scope="function")
def test_nationality(session):
    nationality1 = utility_models.Nationality(kr_name="대한민국")
    nationality2 = utility_models.Nationality(kr_name="미국")
    session.add(nationality1)
    session.add(nationality2)
    session.commit()
    return nationality1, nationality2
