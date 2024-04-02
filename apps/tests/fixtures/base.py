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


DATABASE_URL = f"postgresql+psycopg2://postgres:{settings.DB_ROOT_PASSWORD}@maindb:5432/{settings.TEST_DB}"

engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if not database_exists(engine.url):
    create_database(engine.url)

ModelBase.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def session():
    ModelBase.metadata.drop_all(bind=engine)
    ModelBase.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    # app에서 사용하는 DB를 오버라이드하는 부분
    app.dependency_overrides[get_db] = override_get_db

    def get_test_token():
        with TestClient(app) as client:
            login_data = {
                "username": "test@example.com",
                "password": "test_password",
            }
            response = client.post("v1/token", data=login_data)
            tokens = response.json()
            access_token = tokens["access_token"]
            return access_token

    # 테스트 클라이언트 생성
    test_client = TestClient(app)

    # 모든 요청에 인증 토큰 추가
    test_token = get_test_token()
    test_client.headers = {
        **test_client.headers,
        "Authorization": f"Bearer {test_token}",
    }

    yield test_client
