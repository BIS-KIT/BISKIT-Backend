from typing import Generator
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# 환경 변수나 설정에서 정보 가져오기
# 이 예제에서는 .env 파일에서 가져왔다고 가정
DATABASE_URL = f"postgresql+psycopg2://postgres:{settings.DB_ROOT_PASSWORD}@maindb:5432/{settings.POSTGRES_DB}"

# SQLAlchemy 설정
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 이 후, `SessionLocal()`을 사용하여 새로운 세션을 생성하고 데이터베이스 트랜잭션을 시작할 수 있습니다.


def get_db() -> Generator:
    """
    호출되면 DB 연결하고 작업 완료되면 close
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
