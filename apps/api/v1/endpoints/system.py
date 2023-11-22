from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import crud
from database.session import get_db
from schemas import system as system_schema
from models import system as system_model
from models import user as user_model


router = APIRouter()


@router.get("/systems")
def read_systems(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    systems, total_count = crud.system.get_multi(db=db, skip=skip, limit=limit)
    return systems, total_count


@router.get("/system/{user_id}", response_model=system_schema.SystemReponse)
def get_systems(user_id: int, db: Session = Depends(get_db)):
    check_obj = crud.get_object_or_404(db=db, model=user_model.User, obj_id=user_id)
    system = crud.system.get_by_user_id(db=db, user_id=user_id)
    return system


@router.put("/system/{system_id}", response_model=system_schema.SystemReponse)
def update_system(
    system_id: int, obj_in: system_schema.SystemUpdate, db: Session = Depends(get_db)
):
    check_obj = crud.get_object_or_404(
        db=db, model=system_model.System, obj_id=system_id
    )
    updated_system = crud.system.update(db=db, db_obj=check_obj, obj_in=obj_in)
    return updated_system


@router.get("/reports", response_model=system_schema.ReportListResponse)
def read_reports(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    """
    전체 신고 확인
    """
    reports, total_count = crud.report.get_multi(db=db, skip=skip, limit=limit)
    return {"reports": reports, "total_count": total_count}


@router.get("/report/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    check_obj = crud.get_object_or_404(
        db=db, model=system_model.Report, obj_id=report_id
    )
    report = crud.report.get(db=db, id=report_id)
    return report


@router.get("/report/{report_id}/approve")
def get_report(report_id: int, db: Session = Depends(get_db)):
    """
    신고 내역 승인 테스트용 api(실제 승인은 admin page에서)
    """
    check_obj = crud.get_object_or_404(
        db=db, model=system_model.Report, obj_id=report_id
    )
    report = crud.report.approve_report(db=db, report_id=report_id)
    return report


@router.post("/report", response_model=system_schema.ReportResponse)
def create_reports(obj_in: system_schema.ReportCreate, db: Session = Depends(get_db)):
    check_targeter = crud.get_object_or_404(
        db=db, model=user_model.User, obj_id=obj_in.target_id
    )
    check_reporter = crud.get_object_or_404(
        db=db, model=user_model.User, obj_id=obj_in.reporter_id
    )

    created_obj = crud.report.create(db=db, obj_in=obj_in)
    return created_obj


@router.get("/ban/{user_id}", response_model=system_schema.BanListReponse)
def read_ban_by_user_id(
    user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    check_obj = crud.get_object_or_404(db=db, model=user_model.User, obj_id=user_id)
    ban_list, total_count = crud.ban.read_ban_user(
        db=db, user_id=user_id, skip=skip, limit=limit
    )
    return {"ban_list": ban_list, "total_count": total_count}


@router.post("/ban/{user_id}")
def create_ban(user_id: int, target_id: int, db: Session = Depends(get_db)):
    """
    target_id 사용자 차단
    """
    check_obj = crud.get_object_or_404(db=db, model=user_model.User, obj_id=user_id)
    check_target_obj = crud.get_object_or_404(
        db=db, model=user_model.User, obj_id=target_id
    )
    obj = crud.ban.create(db=db, user_id=user_id, target_id=target_id)
    return obj


@router.delete("/ban")
def remove_ban(ban_ids: List[int], db: Session = Depends(get_db)):
    """
    차단 해제

    - ban_id를 쉼표(,)로 구분해서 넣어주시면 됩니다.
        - ex) [3,5]
    """
    for ban_id in ban_ids:
        check_obj = crud.get_object_or_404(db=db, model=system_model.Ban, obj_id=ban_id)
        obj = crud.ban.remove(db=db, id=ban_id)
    return status.HTTP_204_NO_CONTENT


@router.get("/notices", response_model=system_schema.NoticeListResponse)
def read_notices(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    notices = crud.notice.get_multi(db - db, skip=skip, limit=limit)
    return notices


@router.post("/notice", response_model=system_schema.NoticeResponse)
def create_notice(obj_in: system_schema.NoticeCreate, db: Session = Depends(get_db)):
    check_obj = crud.get_object_or_404(
        db=db, model=user_model.User, obj_id=obj_in.user_id
    )
    if not check_obj.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )

    create_obj = crud.notice.create(db=db, obj_in=obj_in)
    return create_obj


@router.put("/notice/{notice_id}", response_model=system_schema.NoticeResponse)
def create_notice(
    notice_id: int,
    user_id: int,
    obj_in: system_schema.NoticeUpdate,
    db: Session = Depends(get_db),
):
    check_obj = crud.get_object_or_404(db=db, model=user_model.User, obj_id=user_id)
    if not check_obj.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    check_notice = crud.get_object_or_404(
        db=db, model=system_model.Notice, obj_id=notice_id
    )
    updated_notice = crud.notice.update(db=db, db_obj=check_notice, obj_in=obj_in)
    return updated_notice


@router.delete("/notice/{notice_id}")
def remove_notice(user_id: int, notice_id: int, db: Session = Depends(get_db)):
    check_obj = crud.get_object_or_404(db=db, model=user_model.User, obj_id=user_id)
    if not check_obj.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    check_notice = crud.get_object_or_404(
        db=db, model=system_model.Notice, obj_id=notice_id
    )
    delete_notice = crud.notice.remove(db=db, id=check_notice.id)
    return status.HTTP_204_NO_CONTENT
