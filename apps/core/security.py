from datetime import datetime, timedelta
from typing import Any, Union, Optional, Annotated
import secrets

from jose import jwt, JWTError
from firebase_admin import auth
from fastapi import HTTPException, Header, status, Depends, Security
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

import crud
from database.session import get_db
from schemas.user import Token, TokenData
from models.user import User
from core.config import settings

security = HTTPBasic()
bearer_security = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    JWT 토큰을 생성한다.

    Args:
    - data: JWT에 포함될 정보.
    - expires_delta: 토큰의 유효기간.

    Returns:
    - 생성된 JWT 토큰 문자열.
    """
    ...
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_id_token(token: str) -> dict:
    """
    Firebase 토큰을 검증한다.

    Args:
    - token: 검증할 Firebase 토큰.

    Returns:
    - 검증된 토큰의 정보를 포함하는 사전.
    """
    ...
    try:
        # Firebase 토큰을 검증
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=403, detail="Invalid authentication credentials"
        )


def get_user_by_fb(authorization: Optional[str] = Header(None)) -> dict:
    """
    Firebase 토큰을 사용하여 사용자 정보를 검색한다.

    Args:
    - authorization: Bearer 형식의 Firebase 토큰.

    Returns:
    - 검증된 사용자의 정보를 포함하는 사전.
    """
    if not authorization:
        raise HTTPException(status_code=403, detail="Unauthorized")
    # Bearer 토큰에서 실제 토큰 분리
    token_prefix, firebase_token = authorization.split(" ")
    if token_prefix != "Bearer":
        raise HTTPException(
            status_code=403, detail="Invalid authentication token format"
        )

    return verify_id_token(firebase_token)


async def get_current_user(token: str):
    """
    현재의 JWT 토큰을 사용하여 사용자 정보를 검색한다.

    Args:
    - token: 검증할 JWT 토큰.

    Returns:
    - 검증된 사용자의 정보를 포함하는 User 객체.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.user.get_by_email(db=get_db(), email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    현재 활성화된 사용자를 반환한다.

    Args:
    - current_user: 검증된 현재 사용자 객체.

    Returns:
    - 활성화된 사용자의 정보를 포함하는 User 객체.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_token(authorization: str = Header(...)) -> str:
    """
    헤더에서 JWT 토큰을 추출합니다.

    Args:
    - authorization (str): 'Bearer [토큰]' 형식의 인증 헤더.

    Returns:
    - str: 추출된 JWT 토큰 문자열.

    헤더 예시:
    Authorization: Bearer [YOUR_JWT_TOKEN]
    """

    token_prefix, token = authorization.split(" ")
    if token_prefix != "Bearer":
        raise HTTPException(status_code=403, detail="Invalid token format")
    return token


def get_admin(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    correct_username = secrets.compare_digest(credentials.username, settings.docs_user)
    correct_password = secrets.compare_digest(credentials.password, settings.docs_pw)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
