import pandas as pd
from sqlalchemy.orm import Session
from models.utility import Language, Nationality
from database.session import SessionLocal


# B4:C147 범위 추출 (0부터 시작하는 인덱스를 기준으로)
# B는 2번째 열, C는 3번째 열이라고 가정합니다.
# 1번 시트에서 "B4:C147" 범위의 데이터 가져오기
subset1 = pd.read_excel("DataSet.xlsx", sheet_name=0, header=None).iloc[3:147, 1:3]

# 2번 시트에서 "B4:D250" 범위의 데이터 가져오기
subset2 = pd.read_excel("DataSet.xlsx", sheet_name=1, header=None).iloc[3:250, 1:4]


def get_nationality(subset: pd.DataFrame):
    db = SessionLocal()
    try:
        for _, row in subset.iterrows():
            kr_name = str(row[subset.columns[0]])
            en_name = str(row[subset.columns[1]])
            code = str(row[subset.columns[2]])
            # 해당 국적이 이미 DB에 있는지 확인
            existing_nationality = (
                db.query(Nationality).filter_by(kr_name=kr_name).first()
            )

            # 없으면 새로 추가
            if not existing_nationality:
                nationality = Nationality(kr_name=kr_name, en_name=en_name, code=code)
                db.add(nationality)
            else:
                # 이미 존재한다면 업데이트
                existing_nationality.kr_name = kr_name
                existing_nationality.en_name = en_name
                existing_nationality.code = code

        db.commit()
    except Exception as e:
        print(f"Error: {e}")  # 오류 메시지 출력
        db.rollback()
    finally:
        db.close()


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
get_language(subset1)
get_nationality(subset2)
