from database.session import SessionLocal
from models.utility import Nationality

session = SessionLocal()

try:
    # Nationality 테이블의 모든 레코드를 조회합니다.
    nationalities = session.query(Nationality).all()

    for nationality in nationalities:
        # 각 레코드의 'code' 필드 값을 소문자로 변환합니다.
        nationality.code = nationality.code.lower()

    # 변환된 값을 데이터베이스에 저장합니다.
    session.commit()

finally:
    session.close()
