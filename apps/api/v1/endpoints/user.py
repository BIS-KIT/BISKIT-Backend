from typing import Any, List, Optional, Dict
from random import randint
from datetime import timedelta
import re

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Header,
    UploadFile,
    Form,
    File,
)
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from sqlalchemy.exc import IntegrityError

import crud
from log import log_error
from schemas.user import (
    Token,
    UserCreate,
    UserResponse,
    RefreshToken,
    PasswordChange,
    PasswordUpdate,
    EmailCertificationIn,
    EmailCertificationCheck,
    UserLogin,
    ConsentCreate,
    UserRegister,
    UserUniversityCreate,
    UserNationalityCreate,
    StudentVerificationCreate,
    StudentVerificationBase,
    StudentVerificationUpdate,
    VerificationStatus,
    ConsentBase,
    ConsentResponse,
    UserUniversityBase,
    UserUniversityUpdate,
)
from models.user import User
from core.security import (
    get_current_token,
    create_access_token,
    get_user_by_fb,
    create_refresh_token,
    get_current_user,
)
from database.session import get_db
from core.config import settings

router = APIRouter()


@router.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    사용자 목록을 반환합니다.

    **파라미터**

    * `skip`: 건너뛸 항목의 수
    * `limit`: 반환할 최대 항목 수

    **반환**

    * 사용자 목록
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    if users is None:
        raise HTTPException(status_code=404, detail="Users not found")
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 목록을 반환합니다.

    **파라미터**

    * `skip`: 건너뛸 항목의 수
    * `limit`: 반환할 최대 항목 수

    **반환**

    * 사용자 목록
    """
    users = crud.user.get(db=db, id=user_id)
    if users is None:
        raise HTTPException(status_code=404, detail="Users not found")
    return users


@router.delete("/user/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 삭제 API
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.user.remove(db, id=user_id)


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    현재 사용자의 정보를 가져옵니다.

    인자:
    - current_user (User): 현재 인증된 사용자.

    반환값:
    - dict: 인증된 사용자의 정보.
    """
    return current_user


@router.post("/register/", response_model=Dict[str, Any])
def register_user(
    user_in: UserRegister,
    db: Session = Depends(get_db),
):
    """
    이메일과 비밀번호를 사용하여 새 사용자를 등록합니다.

    Args:
    - user_in (UserCreate): 사용자의 이메일 및 비밀번호.
    - db (Session): 데이터베이스 세션.

    Returns:
    - dict: 새로 등록된 사용자의 ID와 이메일.
    """

    new_user = None
    consent_obj = None
    user_university_obj = None
    user_nationally_obj_list = []

    # 데이터베이스에서 이메일로 사용자 확인
    db_user = crud.user.get_by_email(db=db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=409, detail="User already registered.")

    password = user_in.password

    if not (8 <= len(password) <= 16):
        raise HTTPException(
            status_code=400, detail="Password must be 8-16 characters long"
        )

    if not not re.match(
        "^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,16}$", password
    ):
        raise HTTPException(
            status_code=400,
            detail="Password must be include at least one letter, one number, and one special character.",
        )

    hashed_password = crud.get_password_hash(password)

    try:
        obj_in = UserCreate(
            email=user_in.email,
            password=hashed_password,
            name=user_in.name,
            birth=user_in.birth,
            gender=user_in.gender,
        )

        new_user = crud.user.create(db=db, obj_in=obj_in)

        consent = ConsentCreate(
            terms_mandatory=user_in.terms_optional,
            terms_optional=user_in.terms_optional,
            terms_push=user_in.terms_push,
            user_id=new_user.id,
        )

        user_university = UserUniversityCreate(
            department=user_in.department,
            education_status=user_in.education_status,
            is_graduated=user_in.is_graduated,
            university_id=user_in.university_id,
            user_id=new_user.id,
        )

        user_nationally_obj_list = user_in.nationality_ids
        for id in user_nationally_obj_list:
            user_nationally = UserNationalityCreate(
                nationality_id=id, user_id=new_user.id
            )
            user_nationally_obj = crud.user.create_nationally(
                db=db, obj_in=user_nationally
            )

        consent_obj = crud.user.create_consent(db=db, obj_in=consent)
        user_university_obj = crud.user.create_university(db=db, obj_in=user_university)
    except Exception as e:
        if new_user:
            crud.user.remove(db=db, id=new_user.id)
        if consent_obj:
            crud.user.remove_consent(db=db, id=id)
        if user_university_obj:
            crud.user.remove_university(db=db, id=user_university_obj.id)
        if user_nationally_obj_list:
            for id in user_nationally_obj_list:
                crud.user.remove_nationally(db=db, id=id)
        print(e)
        log_error(e)
        raise HTTPException(status_code=500)

    # 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": new_user.email})
    return {
        "id": new_user.id,
        "token": access_token,
        "email": new_user.email,
        "refresh_token": refresh_token,
    }


@router.post("/register/firebase", response_model=UserResponse)
def create_user(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_by_fb),
):
    """
    Firebase 토큰에서의 이메일을 사용하여 새 사용자를 등록합니다.

    인자:
    - db (Session): 데이터베이스 세션.
    - current_user (dict): 현재 인증된 사용자의 데이터.
    - authorization: Bearer 형식의 Firebase 토큰.

    반환값:
    - dict: 새로 등록된 사용자의 ID와 이메일.
    """
    user_email = current_user.get("email")  # Firebase 토큰에서 이메일 가져오기
    if not user_email:
        raise HTTPException(
            status_code=400, detail="Email not found in Firebase token."
        )

    # 데이터베이스에서 이메일로 사용자 확인
    db_user = crud.user.get_by_email(db=db, email=user_email)
    if db_user:
        raise HTTPException(status_code=409, detail="User already registered.")

    # 새로운 사용자 생성 및 저장
    obj_in = UserCreate(email=user_email)
    new_user = crud.user.create(db=db, obj_in=obj_in)
    return {"id": new_user.id, "email": new_user.email}


@router.post("/login/firebase", response_model=Token)
async def login_for_access_token_firebase(authorization: str = Depends(get_user_by_fb)):
    """
    Firebase 인증 정보를 사용하여 사용자를 인증하고, JWT 토큰을 반환합니다.

    Firebase 인증을 통해 사용자의 이메일 주소를 확인하고, 해당 이메일을 주체로하는 JWT 토큰을 생성합니다.
    생성된 토큰은 클라이언트에 반환되어 다른 API 엔드포인트에 대한 인증 수단으로 사용될 수 있습니다.

    Args:
    - authorization (str): Bearer 형식의 Firebase 토큰.

    Returns:
    - Token: 생성된 JWT 토큰을 포함하는 객체.
    """
    email = authorization["email"]
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Dict[str, Any])
def login_for_access_token(login_obj: UserLogin, db: Session = Depends(get_db)):
    """
    로그인을 위한 엑세스 토큰을 발급

    사용자로부터 이메일(또는 사용자 이름)과 비밀번호를 받아, 해당 정보가 올바른지 검증
    올바른 사용자 정보일 경우, JWT 형식의 엑세스 토큰을 발행하여 반환

    Parameters:
    - db (Session): 데이터베이스 세션 객체.

    Returns:
    - dict: 엑세스 토큰,리프레쉬 토큰과 토큰 유형을 포함

    Raises:
    - HTTPException: 사용자 정보가 잘못되었거나, 해당 사용자가 데이터베이스에 없는 경우 발생.
    """

    # 데이터베이스에서 사용자 조회
    user = crud.user.get_by_email(db=db, email=login_obj.email)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email")
    # 비밀번호 검증
    if not crud.verify_password(login_obj.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    # 토큰 생성 및 반환
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/token/refresh/", response_model=Token)
async def refresh_token(token: str = Depends(get_current_token)):
    """
    기존 토큰을 새로고침합니다.

    인자:
    - token (str): 현재 refresh_token.

    반환값:
    - Token: 새로고침된 토큰.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Could not validate email")
        token_expired = payload.get("exp")
        if token_expired:
            raise HTTPException(status_code=400, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=400, detail="Could not validate credentials")

    # 새로운 access_token 생성
    access_token = create_access_token(data={"email": email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/token/validate/")
def validate_token(token: str = Depends(get_current_token)):
    """
    제공된 토큰을 검증합니다.

    인자:
    - token (str): 'Bearer [토큰]' 형식의 인증 헤더.

    반환값:
    - dict: 토큰의 검증 상태.
    """

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            credentials_exception = HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            raise credentials_exception
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 토큰이 유효하면 아래 메시지 반환
    return {"detail": "Token is valid"}


@router.post("/change-password/")
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    사용자의 비밀번호를 변경합니다.

    인자:
    - password_data (PasswordChange): 변경하려는 비밀번호에 대한 데이터.
    - db (Session): 데이터베이스 세션.
    - current_user (User): 현재 인증된 사용자.

    반환값:
    - dict: 비밀번호 변경 상태 메시지.
    """
    if not current_user:
        raise HTTPException(status_code=400, detail="User not found")

    if not crud.verify_password(password_data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    if password_data.new_password != password_data.new_password_check:
        raise HTTPException(status_code=400, detail="New passwords do not match")

    user_in = PasswordUpdate(password=password_data.new_password)
    updated_user = crud.user.update(db, db_obj=current_user, obj_in=user_in)

    return {"detail": "Password changed successfully"}


@router.post("/check-email/")
def check_mail_exists(email: str, db: Session = Depends(get_db)):
    if not "@" in email:
        raise HTTPException(status_code=409, detail="This is not Email Form.")

    check_email = crud.user.get_by_email(db=db, email=email)
    if check_email:
        raise HTTPException(status_code=409, detail="Email already registered.")
    return {"status": "Email is available."}


@router.post("/certificate/")
async def certificate_email(
    cert_in: EmailCertificationIn, db: Session = Depends(get_db)
):
    if not "@" in cert_in.email:
        raise HTTPException(status_code=409, detail="This is not Email Form.")

    check_user = crud.user.get_by_email(db=db, email=cert_in.email)
    if check_user:
        raise HTTPException(status_code=409, detail="Email already registered.")

    certification = str(randint(100000, 999999))
    user_cert = EmailCertificationCheck(
        email=cert_in.email, certification=certification
    )

    # DB에 인증 데이터 저장
    try:
        certi = crud.user.create_email_certification(db, obj_in=user_cert)
        if crud.send_email(certification, cert_in.email):
            return {
                "result": "success",
                "email": cert_in.email,
                "certification": certification,
            }
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists.")
    except Exception as e:
        log_error(e)
        crud.user.remove_email_certification(db, db_obj=certi)
        return {"result": "fail"}


@router.post("/certificate/check/")
async def certificate_check(
    cert_check: EmailCertificationCheck, db: Session = Depends(get_db)
):
    user_cert = crud.user.get_email_certification(
        db, email=cert_check.email, certification=cert_check.certification
    )
    if user_cert:
        # db.delete(user_cert)
        # db.commit()
        return {"result": "success", "email": cert_check.email}
    return {"result": "fail"}


@router.post("/user/student-card", response_model=StudentVerificationBase)
def student_varification(
    student_card: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
):
    user = crud.user.get(db=db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")

    obj_in = StudentVerificationBase(
        student_card=student_card,
        user_id=user_id,
    )

    try:
        user_verification = crud.user.create_verification(db=db, obj_in=obj_in)
    except Exception as e:
        log_error(e)
        print(e)
        raise HTTPException(status_code=500)
    return user_verification


@router.get("/user/{user_id}/student-card", response_model=StudentVerificationBase)
def student_varification(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = crud.user.get(db=db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")

    db_obj = crud.user.get_verification(db=db, user_id=user_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="StudentVerification not found")
    return db_obj


@router.post("/user/{user_id}/student-card/approve")
def approve_varification(
    user_id: int,
    db: Session = Depends(get_db),
):
    verification = crud.user.get_verification(db=db, user_id=user_id)
    if verification is None:
        raise HTTPException(status_code=404, detail="StudentVerification not found")

    obj_in = StudentVerificationUpdate(
        verification_status=VerificationStatus.VERIFIED.value
    )
    update_verification = crud.user.update_verification(
        db=db, db_obj=verification, obj_in=obj_in
    )
    return update_verification


@router.get("/user/{user_id}/consent", response_model=ConsentResponse)
def get_user_consent(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    consent = crud.user.get_consent(db=db, user_id=user_id)
    if not consent:
        raise HTTPException(status_code=400, detail="Consent not found")
    return consent


@router.delete("/user/{user_id}/consent", response_model=ConsentResponse)
def delete_user_consent(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    consent = crud.user.get_consent(db=db, user_id=user_id)
    if not consent:
        raise HTTPException(status_code=400, detail="Consent not found")

    db_obj = crud.user.remove_consent(db=db, id=consent.id)
    return db_obj


# @router.put("/user/{user_id}/consent")
# def update_user_consent(
#     user_id: int,
#     db: Session = Depends(get_db),
# ):
#     pass


@router.get("/user/{user_id}/university", response_model=UserUniversityBase)
def get_user_university(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user_university = crud.user.get_university(db=db, user_id=user_id)
    if not user_university:
        raise HTTPException(status_code=400, detail="user_university not found")
    return user_university


@router.delete("/user/{user_id}/university", response_model=UserUniversityBase)
def delete_user_university(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user_university = crud.user.get_university(db=db, user_id=user_id)
    if not user_university:
        raise HTTPException(status_code=400, detail="user_university not found")

    db_obj = crud.user.remove_university(db=db, id=user_university.id)
    return db_obj


@router.put("/user/{user_id}/university", response_model=UserUniversityBase)
def update_user_university(
    user_id: int,
    user_univeristy: UserUniversityUpdate,
    db: Session = Depends(get_db),
):
    exsisting_user_university = crud.user.get_university(db=db, user_id=user_id)
    if not exsisting_user_university:
        raise HTTPException(status_code=404, detail="UserUniversity not found")

    update_user_univer = crud.user.update_university(
        db=db, db_obj=exsisting_user_university, obj_in=user_univeristy
    )
    return update_user_univer
