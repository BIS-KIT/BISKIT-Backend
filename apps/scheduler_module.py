from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database.session import SessionLocal
from models import meeting as metting_model
import crud
from log import scheduler_logger


def meeting_active_check():
    db = SessionLocal()
    all_active_meeting = crud.meeting.get_all_active_meeting(db=db)
    current_time = datetime.now()

    deactive_count = 0
    for meeting in all_active_meeting:
        if meeting.meeting_time < current_time:
            meeting.is_active = False
            deactive_count += 1

    db.commit()
    scheduler_logger.warning(f"{deactive_count} mettings deactive")
    return


def user_remove_after_seven():
    db = SessionLocal()
    deactive_users = crud.user.get_deactive_users(db=db)
    current_date = datetime.now().date()

    deleted_count = 0
    for user in deactive_users:
        # 사용자의 비활성화 날짜가 현재 날짜보다 일주일 이상 이전인지 확인
        if user.deactive_time and current_date - user.deactive_time.date() > timedelta(
            days=7
        ):
            db.delete(user)  # 사용자 삭제
            deleted_count += 1

    db.commit()
    scheduler_logger.warning(f"{deleted_count} user(s) deleted")
    return


def meeting_time_alarm():
    db = SessionLocal()

    current_time = datetime.now()
    meeting_id_list = crud.meeting.get_meeting_with_hour(
        db=db, current_time=current_time
    )

    for id in meeting_id_list:
        crud.alarm.meeting_time_alarm(db=db, meeting_id=id)

    return None
