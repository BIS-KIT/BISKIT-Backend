import pandas as pd
from sqlalchemy.orm import Session
from models.utility import Language
from database.session import SessionLocal

df = pd.read_excel("사용언어_국적_학교_리스트.xlsx", header=None)

# B4:C147 범위 추출 (0부터 시작하는 인덱스를 기준으로)
# B는 2번째 열, C는 3번째 열이라고 가정합니다.
subset = df.iloc[3:147, 1:3]


def get_language(subset: pd.DataFrame):
    db = SessionLocal()
    try:
        for _, row in subset.iterrows():
            kr_name = row[subset.columns[0]]
            en_name = row[subset.columns[1]]

            # 해당 언어가 이미 DB에 있는지 확인
            existing_language = db.query(Language).filter_by(kr_name=kr_name).first()

            # 없으면 새로 추가
            if not existing_language:
                language = Language(kr_name=kr_name, en_name=en_name)
                db.add(language)
            else:
                # 이미 존재한다면 업데이트
                existing_language.kr_name = kr_name
                existing_language.en_name = en_name

        db.commit()
    except Exception as e:
        print(f"Error: {e}")  # 오류 메시지 출력
        db.rollback()
    finally:
        db.close()


# 사용법
get_language(subset)
