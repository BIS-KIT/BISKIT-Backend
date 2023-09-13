from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.profile import Profile
from schemas.profile import ProfileCreate, ProfileUpdate


class CRUDProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    """
    CRUD operations for User model.
    """

    def get_by_user_id(self, db: Session, *, user_id: str) -> Optional[Profile]:
        return db.query(Profile).filter(Profile.user_id == user_id).first()

    def create(self, db: Session, *, obj_in: ProfileCreate, user_id: int) -> Profile:
        """
        Create a new user.

        Args:
            db: Database session instance.
            obj_in: User creation schema containing user details.

        Returns:
            Created User instance.
        """
        if not user_id:
            raise ValueError("There is no user_id")

        db_obj = Profile(**obj_in.dict(), user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Profile,
        obj_in: Union[ProfileUpdate, Dict[str, Any]]
    ) -> Profile:
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

        return super().update(db, db_obj=db_obj, obj_in=update_data)


profile = CRUDProfile(Profile)
