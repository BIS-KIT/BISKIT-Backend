from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Header
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from firebase_admin import auth

import crud
from schemas.user import Token
from core.security import (
    get_user_by_fb,
    get_current_token,
    create_access_token,
    verify_password,
    get_password_hash,
)
from database.session import get_db

router = APIRouter()


@router.get("/users/me", response_model=dict)
def read_users_me(current_user: auth.UserRecord = Depends(get_user_by_fb)):
    return current_user.__dict__


@router.post("/users/", response_model=dict)
def create_user(
    db: Session = Depends(get_db), current_user: dict = Depends(get_user_by_fb)
):
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
    # Here, verify the token, get the user information and recreate the token
    # For demonstration, we'll just create a new token with a dummy email
    access_token = create_access_token(data={"email": "user@example.com"})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/token/validate/")
def validate_token(token: str = Depends(get_current_token)):
    # Just by getting here, the token is already valid
    # because the `get_current_token` dependant would've rejected invalid tokens
    return {"detail": "Token is valid"}


@router.post("/logout/")
def logout(token: str = Depends(get_current_token)):
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
    user = crud.user.get_by_email(db, email=current_user_email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # 3. Check the old password against the stored hashed password
    if not verify_password(old_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    # 4. If it matches, hash and store the new password
    hashed_new_password = get_password_hash(new_password)
    user.password = hashed_new_password
    db.add(user)
    db.commit()

    return {"detail": "Password changed successfully"}
    return {"detail": "Password changed successfully"}
