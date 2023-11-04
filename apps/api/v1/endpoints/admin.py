from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

import crud
from database.session import get_db
from schemas.profile import StudentVerificationUpdate, ReultStatusEnum

router = APIRouter()


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
