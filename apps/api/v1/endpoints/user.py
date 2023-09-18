from typing import Any, List, Optional, Dict
from random import randint
from datetime import timedelta

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Body, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from sqlalchemy.exc import IntegrityError

import crud
from schemas.user import (
    Token,
    UserCreate,
    UserResponse,
    RefreshToken,
    PasswordChange,
    PasswordUpdate,
    EmailCertificationIn,
    EmailCertificationCheck,
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


@router.post("/register/", response_model=dict)
def register_user(
    user_in: UserCreate,
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
    print(user_in)

    # 데이터베이스에서 이메일로 사용자 확인
    db_user = crud.user.get_by_email(db=db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=409, detail="User already registered.")

    hashed_password = crud.get_password_hash(user_in.password)

    obj_in = UserCreate(email=user_in.email, password=hashed_password)

    new_user = crud.user.create(db=db, obj_in=obj_in)

    # 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    return {"id": new_user.id, "token": access_token, "email": new_user.email}


@router.post("/register/firebase", response_model=dict)
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
def login_for_access_token(login_obj: UserCreate, db: Session = Depends(get_db)):
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

    if password_data.new_password != password_data.new_password_check:
        raise HTTPException(status_code=400, detail="New passwords do not match")

    if not crud.verify_password(password_data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    user_in = PasswordUpdate(password=password_data.new_password)
    updated_user = crud.user.update(db, db_obj=current_user, obj_in=user_in)

    return {"detail": "Password changed successfully"}

@router.post("/check-email/")
def check_mail_exists(email:str, db:Session=Depends(get_db)):
    check_email = crud.user.get_by_email(db=db, email=email)
    if check_email:
        raise HTTPException(status_code=409, detail="Email already registered.")
    return {"status": "Email is available."}


@router.post("/certificate/")
async def certificate_email(
    cert_in: EmailCertificationIn, db: Session = Depends(get_db)
):
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
        db.delete(user_cert)
        db.commit()
        return {"result": "success", "email": cert_check.email}
    return {"result": "fail"}
