from typing import Any, Optional, List
from sqlalchemy import func, desc, asc, extract
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from models.system import Ban, Report
from schemas.system import BanCreate, ReportCreateIn

from log import log_error
from crud.base import CRUDBase
import crud
from models import system as system_models
from schemas import system as system_schemas
from schemas.enum import ReultStatusEnum


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
    def create(self, db: Session, *, obj_in: system_schemas.ReportCreate) -> Report:
        obj_data = obj_in.model_dump()
        obj_data_in = system_schemas.ReportCreateIn(**obj_data)
        return super().create(db, obj_in=obj_data_in)

    def get_by_user_id(self, db: Session, user_id: int):
        obj = (
            db.query(Report)
            .filter(
                Report.content_id == user_id,
                Report.content_type == "User",
                Report.status == ReultStatusEnum.APPROVE.value,
            )
            .all()
        )
        return obj

    def approve_report(self, db: Session, report_id: int):
        approve_obj = db.query(Report).filter(Report.id == report_id).first()
        approve_obj.status = ReultStatusEnum.APPROVE.value
        db.commit()
        if approve_obj.content_type == "User":
            alarm = crud.alarm.report_alarm(db=db, target_id=approve_obj.content_id)

        return approve_obj


class CRUDNotice(
    CRUDBase[
        system_models.Notice, system_schemas.NoticeCreate, system_schemas.NoticeUpdate
    ]
):
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List:
        total_count = db.query(self.model).count()
        return (
            db.query(self.model)
            .order_by(self.model.created_time.desc())
            .offset(skip)
            .limit(limit)
            .all(),
            total_count,
        )


class CRUDBan(
    CRUDBase[system_models.Ban, system_schemas.BanCreate, system_schemas.BanUpdate]
):
    def read_ban_user(
        self, db: Session, user_id: int, skip: int, limit: int
    ) -> List[Ban]:
        query = db.query(Ban).filter(Ban.reporter_id == user_id)
        total_count = query.count()
        return query.offset(skip).limit(limit).all(), total_count

    def get_target_ids(self, db: Session, user_id: int) -> List[int]:
        ban_list = db.query(Ban).filter(Ban.reporter_id == user_id).all()
        target_id_list = [ban.target_id for ban in ban_list]
        return target_id_list

    def get_ban(self, db: Session, user_id: int, target_id: int):
        obj = (
            db.query(Ban)
            .filter(Ban.target_id == target_id, Ban.reporter_id == user_id)
            .first()
        )
        return obj

    def delete_ban_with_id(self, db: Session, reporter_id: int, target_id: int):
        obj = db.query(Ban).filter(Ban.reporter_id == reporter_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"Ban is not found")
        db.delete(obj)
        db.commit()
        return obj


class CRUDContact(
    CRUDBase[
        system_models.Contact,
        system_schemas.ContactCreate,
        system_schemas.ContactCreate,
    ]
):
    pass


system = CRUDSystem(system_models.System)
report = CRUDReport(system_models.Report)
ban = CRUDBan(system_models.Ban)
notice = CRUDNotice(system_models.Notice)
contact = CRUDContact(system_models.Contact)
