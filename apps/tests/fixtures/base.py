import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy_utils import database_exists, create_database

from main import create_app
from core.config import settings
from database.session import get_db
from models.base import ModelBase


DATABASE_URL = f"postgresql+psycopg2://postgres:{settings.DB_ROOT_PASSWORD}@{settings.POSTGRES_HOST}:5432/{settings.TEST_DB}"

engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

ModelBase.metadata.drop_all(bind=engine)
ModelBase.metadata.create_all(bind=engine)

if not database_exists(engine.url):
    create_database(engine.url)


test_app = create_app()


def get_test_token():
    from core.security import create_access_token
    from ..factories import UserFactory

    test_user = UserFactory()

    login_data = {"username": test_user.email, "auth_method": "email"}

    access_token = create_access_token(data=login_data)
    return access_token


@pytest.fixture(scope="session")
def client():
    db = TestingSessionLocal()

    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    test_app.dependency_overrides[get_db] = override_get_db

    # 테스트 클라이언트 생성
    test_client = TestClient(test_app)

    # 모든 요청에 인증 토큰 추가
    test_token = get_test_token()
    test_client.headers = {
        **test_client.headers,
        "Authorization": f"Bearer {test_token}",
    }

    yield test_client
