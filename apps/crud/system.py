from typing import Any, Optional, List
from sqlalchemy import func, desc, asc, extract
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from models.system import Ban
from schemas.system import BanCreate

from log import log_error
from crud.base import CRUDBase
from models import system as system_models
from schemas import system as system_schemas


class CRUDSystem(
    CRUDBase[
        system_models.System, system_schemas.SystemCreate, system_schemas.SystemUpdate
    ]
):
    def get_by_user_id(self, db: Session, user_id: int) -> system_models.System | None:
        return (
            db.query(system_models.System)
            .filter(system_models.System.user_id == user_id)
            .first()
        )

    def create_with_default_value(self, db: Session, user_id: int):
        obj_in = system_schemas.SystemCreate(user_id=user_id)
        return super().create(db=db, obj_in=obj_in)


class CRUDReport(
    CRUDBase[
        system_models.Report, system_schemas.ReportCreate, system_schemas.ReportUpdate
    ]
):
    pass


class CRUDNotice(
    CRUDBase[
        system_models.Notice, system_schemas.NoticeCreate, system_schemas.NoticeUpdate
    ]
):
    pass


class CRUDBan(
    CRUDBase[system_models.Ban, system_schemas.BanCreate, system_schemas.BanUpdate]
):
    def create(self, db: Session, *, user_id: int, target_id: int) -> Ban:
        obj_in = BanCreate(reporter_id=user_id, target_id=target_id)
        return super().create(db=db, obj_in=obj_in)

    def read_ban_user(
        self, db: Session, user_id: int, skip: int, limit: int
    ) -> List[Ban]:
        query = db.query(Ban).filter(Ban.reporter_id == user_id)
        total_count = query.count()
        return query.offset(skip).limit(limit).all(), total_count


system = CRUDSystem(system_models.System)
report = CRUDReport(system_models.Report)
ban = CRUDBan(system_models.Ban)
notice = CRUDNotice(system_models.Notice)
