from typing import Any, Optional
from sqlalchemy import func, desc, asc, extract
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from log import log_error
from crud.base import CRUDBase
from models.system import System, Report, Notice
from schemas.system import (
    SystemCreate,
    SystemUpdate,
    ReportCreate,
    ReportUpdate,
    NoticeCreate,
    NoticeUpdate,
)


class CRUDSystem(CRUDBase[System, SystemCreate, SystemUpdate]):
    def get_by_user_id(self, db: Session, user_id: Any) -> System | None:
        return db.query(System).filter(System.user_id == user_id).first()


class CRUDReport(CRUDBase[Report, ReportCreate, ReportUpdate]):
    pass


class CRUDNotice(CRUDBase[Notice, NoticeCreate, NoticeUpdate]):
    pass


system = CRUDSystem(System)
report = CRUDReport(Report)