from datetime import datetime, timedelta
from typing import Any, Union, Optional, Annotated

from jose import jwt, JWTError
from firebase_admin import auth
from passlib.context import CryptContext
from fastapi import HTTPException, Header, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import crud
from database.session import get_db
from schemas.user import Token, TokenData
from models.user import User
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
        expire = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    주어진 패스워드와 해시된 패스워드가 일치하는지 확인한다.

    Args:
    - plain_password: 검증할 패스워드.
    - hashed_password: 해시된 패스워드.

    Returns:
    - 패스워드가 일치하면 True, 그렇지 않으면 False.
    """
    ...
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    패스워드를 해싱한다.

    Args:
    - password: 해싱할 패스워드.

    Returns:
    - 해싱된 패스워드 문자열.
    """
    return pwd_context.hash(password)


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


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
    현재 Bearer 토큰을 추출한다.

    Args:
    - authorization: 헤더에서 가져온 인증 정보.

    Returns:
    - 추출된 JWT 토큰 문자열.
    """

    token_prefix, token = authorization.split(" ")
    if token_prefix != "Bearer":
        raise HTTPException(status_code=403, detail="Invalid token format")
    return token
