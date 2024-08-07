from datetime import datetime, timedelta
from typing import Any, Dict, Annotated
import secrets

from jose import jwt, JWTError, ExpiredSignatureError
from firebase_admin import auth
from fastapi import HTTPException, Header, status, Depends, Security
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy.orm import Session

import crud
from database.session import get_db
from schemas.user import Token, TokenData
from models.user import User
from core.config import settings

security = HTTPBasic()
bearer_security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/token")


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


def create_refresh_token(data: dict):
    """
    JWT 리프레시 토큰을 생성한다.

    Args:
    - data: JWT에 포함될 정보.

    Returns:
    - 생성된 JWT 리프레시 토큰 문자열.
    """
    ...
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM
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

    if not authorization:
        raise HTTPException(status_code=403, detail="Token is missing")

    token_parts = authorization.split(" ")
    if len(token_parts) != 2:
        raise HTTPException(status_code=403, detail="Invalid token format")

    token_prefix, token = token_parts
    if token_prefix != "Bearer":
        raise HTTPException(status_code=403, detail="Invalid token prefix")

    return token


def get_current_user(
    token: str = Depends(get_current_token), db: Session = Depends(get_db)
):
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
        auth_method = payload.get("auth_method")

        if auth_method == "email":
            email = payload.get("sub")
            user = crud.user.get_by_email(db=db, email=email)
        elif auth_method == "sns":
            sns_id = payload.get("sub")
            sns_type = payload.get("sns_type")
            user = crud.user.get_by_sns(db=db, sns_id=sns_id, sns_type=sns_type)
        else:
            raise HTTPException(status_code=400, detail="Unknown auth_method")

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return user


def get_admin(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    correct_username = secrets.compare_digest(credentials.username, settings.DOCS_USER)
    correct_password = secrets.compare_digest(credentials.password, settings.DOCS_PW)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def create_tokens_for_user(user: User) -> Dict[str, Any]:
    """
    주어진 사용자에 대해 액세스 토큰과 리프레시 토큰을 생성하고 반환합니다.

    Args:
        user (User): 토큰을 생성할 사용자 객체.

    Returns:
        Dict[str, Any]: 생성된 토큰과 사용자 정보를 포함하는 딕셔너리.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    if user.email:
        token_data = {"sub": user.email, "auth_method": "email"}
    else:
        token_data = {
            "sub": user.sns_id,
            "sns_type": user.sns_type,
            "auth_method": "sns",
        }

    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data=token_data)

    return {
        "id": user.id,
        "token": access_token,
        "refresh_token": refresh_token,
        "email": user.email,
        "sns_type": user.sns_type,
        "sns_id": user.sns_id,
    }
