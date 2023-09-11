from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, Header
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from firebase_admin import auth

import crud
from schemas.user import Token
from models.user import User
from core.security import (
    get_current_user,
    get_current_token,
    create_access_token,
    get_user_by_fb,
)
from database.session import get_db

router = APIRouter()


@router.get("/users/me", response_model=Dict[str, Any])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    현재 사용자의 정보를 가져옵니다.

    인자:
    - current_user (User): 현재 인증된 사용자.

    반환값:
    - dict: 인증된 사용자의 정보.
    """
    return current_user.__dict__


@router.post("/users/", response_model=dict)
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
        raise HTTPException(status_code=400, detail="User already registered.")

    # 새로운 사용자 생성 및 저장
    obj_in = {"email": user_email}
    new_user = crud.user.create(db=db, obj_in=obj_in)
    return {"id": new_user.id, "email": new_user.email}


@router.post("/token/refresh/", response_model=Token)
def refresh_token(token: str = Depends(get_current_token)):
    """
    기존 토큰을 새로고침합니다.

    인자:
    - token (str): 현재 토큰.

    반환값:
    - Token: 새로고침된 토큰.
    """
    access_token = create_access_token(data={"email": "user@example.com"})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/token/validate/")
def validate_token(token: str = Depends(get_current_token)):
    """
    제공된 토큰을 검증합니다.

    인자:
    - token (str): 검증될 토큰.

    반환값:
    - dict: 토큰의 검증 상태.
    """
    # Just by getting here, the token is already valid
    # because the `get_current_token` dependant would've rejected invalid tokens
    return {"detail": "Token is valid"}


@router.post("/logout/")
def logout(token: str = Depends(get_current_token)):
    """
    사용자를 로그아웃합니다.

    인자:
    - token (str): 사용자의 현재 토큰.

    반환값:
    - dict: 로그아웃 상태 메시지.
    """
    # For JWTs, a stateless logout is just forgetting the token on the client side.
    # For a stateful logout, you need to keep a blacklist of tokens and check against it
    # which isn't shown here.
    return {"detail": "Logged out successfully"}


@router.post("/change-password/")
def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_token),
):
    """
    사용자의 비밀번호를 변경합니다.

    인자:
    - old_password (str): 사용자의 현재 비밀번호.
    - new_password (str): 사용자의 새 비밀번호.
    - db (Session): 데이터베이스 세션.
    - current_user_email (str): 현재 인증된 사용자의 이메일.

    반환값:
    - dict: 비밀번호 변경 상태 메시지.
    """
    user = crud.user.get_by_email(db, email=current_user_email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if not crud.user.verify_password(old_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    hashed_new_password = crud.user.get_password_hash(new_password)
    user.password = hashed_new_password
    db.add(user)
    db.commit()

    return {"detail": "Password changed successfully"}
