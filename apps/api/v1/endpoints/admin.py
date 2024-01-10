from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import crud
from database.session import get_db
from schemas.profile import StudentVerificationUpdate, ReultStatusEnum

router = APIRouter()

templates = Jinja2Templates(directory="/apps/admin/templates/")


@router.post("/student-card/verify/{id}")
def approve_varification(
    id: int,
    action: str,
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 학생증 인증을 승인하거나 거절합니다.

    **인자:**
    - user_id (int): 사용자 ID.
    - db (Session): 데이터베이스 세션.
    - action (str) : Approve or Rejected

    **반환값:**
    - dict: 인증 승인 결과.
    """
    verification = crud.profile.get_verification(db=db, id=id)
    if verification is None:
        raise HTTPException(status_code=404, detail="StudentVerification not found")

    if action == "approve":
        obj_in = StudentVerificationUpdate(
            verification_status=ReultStatusEnum.APPROVE.value
        )
    elif action == "rejected":
        obj_in = StudentVerificationUpdate(
            verification_status=ReultStatusEnum.REJECTED.value
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    update_verification = crud.profile.update_verification(
        db=db, db_obj=verification, obj_in=obj_in
    )

    return RedirectResponse(url="/admin/student-verification/list", status_code=303)


@router.post("/tag/home/display")
def display_home_display_tag(tag_id: int = Form(...), db: Session = Depends(get_db)):
    """
    admin 에서만 쓰일 api 입니다.
    """

    tag = crud.utility.display_tag(db=db, tag_id=tag_id)
    return RedirectResponse(url="/admin/tag/list", status_code=303)


@router.post("/tag/home/hide")
def hide_home_display_tag(tag_id: int = Form(...), db: Session = Depends(get_db)):
    """
    admin 에서만 쓰일 api 입니다.
    """

    tag = crud.utility.hide_tag(db=db, tag_id=tag_id)
    return RedirectResponse(url="/admin/tag/list", status_code=303)


@router.get("/report/{report_id}/approve")
def get_report(report_id: int, db: Session = Depends(get_db)):
    """
    신고 내역 승인 테스트용 api(실제 승인은 admin page에서)
    """
    report = crud.report.approve_report(db=db, report_id=report_id)
    return RedirectResponse(url="/admin/report/list", status_code=303)


@router.get("/admin/meeting/{meeting_id}")
def get_meeting_in_admin(
    request: Request, meeting_id: int, db: Session = Depends(get_db)
):
    meeting = crud.meeting.get(db=db, id=meeting_id)
    # HTML 템플릿에 변수 전달
    return templates.TemplateResponse(
        "report_details.html", {"request": request, "obj": meeting.to_dict()}
    )


@router.get("/admin/review/{review_id}")
def get_review_in_admin(
    request: Request, review_id: int, db: Session = Depends(get_db)
):
    review = crud.review.get(db=db, id=review_id)
    # HTML 템플릿에 변수 전달
    return templates.TemplateResponse(
        "report_details.html", {"request": request, "obj": review.to_dict()}
    )


@router.get("/admin/user/{user_id}")
def get_user_in_admin(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = crud.user.get(db=db, id=user_id)
    # HTML 템플릿에 변수 전달
    return templates.TemplateResponse(
        "report_details.html", {"request": request, "obj": user.to_dict()}
    )
