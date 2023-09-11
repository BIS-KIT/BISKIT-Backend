from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from passlib.context import CryptContext


from crud.base import CRUDBase
from models.user import User
from schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations for User model.
    """

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Retrieve a user by its email.

        Args:
            db: Database session instance.
            email: Email of the user to retrieve.

        Returns:
            User instance if found, else None.
        """
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user.

        Args:
            db: Database session instance.
            obj_in: User creation schema containing user details.

        Returns:
            Created User instance.
        """
        if "password" in obj_in:
            obj_in.password = get_password_hash(obj_in.password)
        db_obj = User(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update a user's details.

        Args:
            db: Database session instance.
            db_obj: User instance to update.
            obj_in: User update schema or dict containing updated details.

        Returns:
            Updated User instance.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by its email and password.

        Args:
            db: Database session instance.
            email: Email of the user to authenticate.
            password: Password for authentication.

        Returns:
            User instance if authentication is successful, else None.
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user = CRUDUser(User)
