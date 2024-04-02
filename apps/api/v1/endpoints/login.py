from typing import Any, List, Optional, Dict, Annotated
from random import randint
from datetime import timedelta, datetime
import re, traceback

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.exc import IntegrityError

import crud
from log import log_error
from schemas.user import (
    Token,
    UserCreate,
    UserResponse,
    PasswordChange,
    PasswordUpdate,
    EmailCertificationIn,
    EmailCertificationCheck,
    UserLogin,
    ConsentCreate,
    UserRegister,
    UserUniversityCreate,
    UserNationalityCreate,
    ConfirmPassword,
)
from models.user import User
from core.security import (
    get_current_token,
    create_access_token,
    create_refresh_token,
    create_tokens_for_user,
)
from database.session import get_db
from core.config import settings

router = APIRouter()


@router.post("/register", response_model=Dict[str, Any])
def register_user(
    user_in: UserRegister,
    db: Session = Depends(get_db),
):
    """
    이메일과 비밀번호를 사용하여 새 사용자를 등록합니다.

    Args:

    - email: EmailStr
    - password: str
    - name: str
    - birth: date
    - gender: str
    - sns_type : str : [kakao, google, apple,...]
    - sns_id : str

    - nationality_ids: List[int]

    - university_id: Optional[int]
    - department: Optional[str] : 소속 선택 ["학부","대학원","교환학생","어학당"]
    - education_status: Optional[str] : 학적 선택 ["재학", "졸업","수료"]

    - terms_mandatory: Optional[bool]
    - terms_optional: Optional[bool]
    - terms_push: Optional[bool]

    Returns:
    - dict: 새로 등록된 사용자의 ID와 이메일.
    """

    exists_check = crud.signup.check_exists(db=db, obj_in=user_in)

    new_user = crud.signup.register_user(db=db, obj_in=user_in)

    return_token_dict = create_tokens_for_user(user=new_user)
    return return_token_dict


@router.post("/token", response_model=Dict[str, Any])
def login_for_openapi(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(get_db),
):

    # 테스트 유저 조건 확인
    if "test" in username:
        # 테스트 유저용 토큰 생성 및 반환
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": "test_user@example.com"}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": "test_user@example.com"})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
        }

    if username:
        user = crud.user.get_by_email(db=db, email=username)
        if not user:
            raise HTTPException(status_code=400, detail="User Not Found")
    else:
        raise HTTPException(status_code=400, detail="Incorrect credentials")

    if not user.is_active:
        raise HTTPException(
            status_code=400, detail="Account in the process of withdrawal"
        )

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
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/login", response_model=Dict[str, Any])
def login_for_access_token(login_obj: UserLogin, db: Session = Depends(get_db)):
    """
    로그인을 위한 엑세스 토큰을 발급

    사용자로부터 이메일(또는 사용자 이름)과 비밀번호를 받아, 해당 정보가 올바른지 검증
    올바른 사용자 정보일 경우, JWT 형식의 엑세스 토큰을 발행하여 반환

    Parameters:
    - email
    - password = None
    - sns_type : str : [kakao, google, apple,...]
    - sns_id = None

    Returns:
    - dict: 엑세스 토큰,리프레쉬 토큰과 토큰 유형을 포함

    Raises:
    - HTTPException: 사용자 정보가 잘못되었거나, 해당 사용자가 데이터베이스에 없는 경우 발생.
    """

    # 데이터베이스에서 사용자 조회
    if login_obj.email:
        user = crud.user.get_by_email(db=db, email=login_obj.email)
        if not user:
            raise HTTPException(status_code=400, detail="User Not Found")
    elif login_obj.sns_type and login_obj.sns_id:
        user = crud.user.get_by_sns(
            db=db, sns_type=login_obj.sns_type, sns_id=login_obj.sns_id
        )
        if not user:
            raise HTTPException(status_code=400, detail="User Not Found")
    else:
        raise HTTPException(status_code=400, detail="Incorrect credentials")

    if not user.is_active:
        raise HTTPException(
            status_code=400, detail="Account in the process of withdrawal"
        )

    # 비밀번호 검증
    ## 일반 로그인
    if login_obj.password and user.password:
        if not crud.verify_password(login_obj.password, user.password):
            raise HTTPException(status_code=400, detail="Incorrect credentials")
    ## SNS 로그인
    elif login_obj.sns_type and login_obj.sns_id:
        if user.sns_type != login_obj.sns_type or user.sns_id != login_obj.sns_id:
            raise HTTPException(status_code=400, detail="Incorrect credentials")
    else:
        raise HTTPException(status_code=400, detail="Incomplete login information")

    if login_obj.fcm_token:
        crud.user.update_fcm_token(
            db=db, user_id=user.id, fcm_token=login_obj.fcm_token
        )

    # 토큰 생성 및 반환
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
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/token/refresh")
async def refresh_token(
    token: str = Depends(get_current_token), db: Session = Depends(get_db)
):
    """
    기존 토큰을 새로고침합니다.

    인자:
    - token (str): 현재 refresh_token.

    반환값:
    - Token: 새로고침된 토큰.
    """
    payload = jwt.decode(
        token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    try:
        payload = jwt.decode(
            token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM]
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
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

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
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/token/validate")
def validate_token(
    token: str = Depends(get_current_token), db: Session = Depends(get_db)
):
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

        auth_method = payload.get("auth_method")

        if auth_method == "email":
            email = payload.get("sub")
            if email is None:
                credentials_exception = HTTPException(
                    status_code=401,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                raise credentials_exception
            user = crud.user.get_by_email(db=db, email=email)
        elif auth_method == "sns":
            sns_id = payload.get("sub")
            sns_type = payload.get("sns_type")
            if sns_id is None:
                credentials_exception = HTTPException(
                    status_code=401,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            user = crud.user.get_by_sns(db=db, sns_id=sns_id, sns_type=sns_type)
        else:
            raise HTTPException(status_code=400, detail="Unknown auth_method")

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 토큰이 유효하면 아래 메시지 반환
    return {"detail": "Token is valid"}


@router.post("/confirm-password")
def check_current_password(obj_in: ConfirmPassword, db: Session = Depends(get_db)):
    """
    user 의 현재 패스워드 확인
    (user_id는 후에 token에서 추출)

    Return
        - 400 : password 틀림
        - 400 : password 없는 유저(sns 가입 유저)
        - 200 : Corrent Password
    """
    check_obj = crud.get_object_or_404(db=db, model=User, obj_id=obj_in.user_id)
    if not check_obj.password:
        raise HTTPException(status_code=400, detail="Password Not Found")

    if not crud.verify_password(obj_in.password, check_obj.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect credentials"
        )
    return status.HTTP_200_OK


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    token: str = Depends(get_current_token),
    db: Session = Depends(get_db),
):
    """
    사용자의 비밀번호를 변경합니다.

    인자:
    - password_data (PasswordChange): 변경하려는 비밀번호에 대한 데이터.
    - db (Session): 데이터베이스 세션.
    - token (str): 현재 access_token
    - current_user (User): 현재 인증된 사용자.

    반환값:
    - dict: 비밀번호 변경 상태 메시지.
    """
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

    user_in = PasswordUpdate(password=password_data.new_password)
    updated_user = crud.user.update(db=db, db_obj=user, obj_in=user_in)

    return {"detail": "Password changed successfully"}


@router.post("/check-email")
def check_mail_exists(email: str, db: Session = Depends(get_db)):
    """
    입력받은 이메일이 이미 존재하는지 확인합니다.

    **인자:**
    - email (str): 확인할 이메일 주소.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - dict: 이메일 사용 가능 여부.
    """
    if not "@" in email:
        raise HTTPException(status_code=409, detail="This is not Email Form.")

    check_email = crud.user.get_by_email(db=db, email=email)
    if check_email:
        raise HTTPException(status_code=409, detail="Email already registered.")
    return {"status": "Email is available."}


@router.post("/change-password/certificate")
async def certificate_email(
    cert_in: EmailCertificationIn, db: Session = Depends(get_db)
):
    """
    패스워드 변경 시 주어진 이메일에 인증번호를 발송합니다.

    **인자:**
    - cert_in (EmailCertificationIn): 인증을 받을 이메일 정보.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - dict: 이메일 인증 결과.
    """
    if not "@" in cert_in.email:
        raise HTTPException(status_code=409, detail="This is not Email Form.")

    check_user = crud.user.get_by_email(db=db, email=cert_in.email)
    if not check_user:
        raise HTTPException(status_code=409, detail="User Not Found")

    certification = str(randint(100000, 999999))
    user_cert = EmailCertificationCheck(
        email=cert_in.email, certification=certification
    )

    # DB에 인증 데이터 저장
    try:
        certi = crud.user.create_email_certification(db=db, obj_in=user_cert)
        if crud.send_email(certification, cert_in.email):
            return {
                "result": "success",
                "email": cert_in.email,
                "certification": certification,
            }
    except Exception as e:
        log_error(e)
        crud.user.remove_email_certification(db=db, db_obj=certi)
        return {"result": "fail"}


@router.post("/change-password/certificate/check")
async def certificate_check_change_pw(
    cert_check: EmailCertificationCheck, db: Session = Depends(get_db)
):
    """
    사용자로부터 입력받은 인증번호를 검증합니다.

    **인자:**
    - cert_check (EmailCertificationCheck): 사용자로부터 입력받은 인증번호.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - dict: 인증번호 검증 결과 및 access token
    """
    user_cert = crud.user.get_email_certification(
        db, email=cert_check.email, certification=str(cert_check.certification)
    )
    if user_cert:

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": cert_check.email, "auth_method": "email"}
        access_token = create_access_token(
            data=token_data, expires_delta=access_token_expires
        )
        # db.delete(user_cert)
        # db.commit()
        return {"result": "success", "email": cert_check.email, "token": access_token}
    return {"result": "fail"}


@router.post("/certificate")
async def certificate_email(
    cert_in: EmailCertificationIn, db: Session = Depends(get_db)
):
    """
    주어진 이메일에 인증번호를 발송합니다.

    **인자:**
    - cert_in (EmailCertificationIn): 인증을 받을 이메일 정보.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - dict: 이메일 인증 결과.
    """
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
        certi = crud.user.create_email_certification(db=db, obj_in=user_cert)
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
        crud.user.remove_email_certification(db=db, db_obj=certi)
        return {"result": "fail"}


@router.post("/certificate/check")
async def certificate_check_log(
    cert_check: EmailCertificationCheck, db: Session = Depends(get_db)
):
    """
    사용자로부터 입력받은 인증번호를 검증합니다.

    **인자:**
    - cert_check (EmailCertificationCheck): 사용자로부터 입력받은 인증번호.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - dict: 인증번호 검증 결과.
    """
    user_cert = crud.user.get_email_certification(
        db, email=cert_check.email, certification=cert_check.certification
    )

    if user_cert:
        return {"result": "success", "email": cert_check.email}
    else:
        return {"result": "fail", "message": "Invalid or expired certification code"}
