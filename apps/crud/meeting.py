from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from fastapi import HTTPException

from crud.base import CRUDBase
import crud
from models.meeting import Meeting, MeetingLanguage, MeetingTag, MeetingTopic, MeetingUser
from schemas.meeting import MeetingCreateUpdate, MeetingItemCreate


class CURDMeeting(CRUDBase[Meeting, MeetingCreateUpdate, MeetingCreateUpdate]):
    def create(self, db: Session, *, obj_in: MeetingCreateUpdate) -> Meeting:
        data = obj_in.model_dump()
        tag_ids = data.pop("tag_ids", [])
        topic_ids = data.pop("topic_ids", [])
        language_ids = data.pop("language_ids", [])

        creater_nationality = crud.user.get_nationality(db=db, user_id=data["creator_id"])
        if creater_nationality:
            if creater_nationality.code == "ko":
                data["korean_count"] += 1
            else:
                data["foreign_count"] += 1

        new_meeting = super().create(db=db, obj_in=MeetingCreateUpdate(**data))
        self.create_meeting_items(db, new_meeting.id, tag_ids, topic_ids, language_ids)
        return new_meeting

    def create_meeting_items(self, db:Session, meeting_id:int,tags_ids:List[int], topic_ids:List[int], language_ids:List[int]):
        if tags_ids:
            for id in tags_ids:
                obj_in = MeetingItemCreate(meeting_id=meeting_id, tag_id=id)
                db_obj = MeetingTag(**obj_in.model_dump())
                db.add(db_obj)
            db.commit()

        if topic_ids:
            for id in topic_ids:
                obj_in = MeetingItemCreate(meeting_id=meeting_id, topic_id=id)
                db_obj = MeetingTopic(**obj_in.model_dump())
                db.add(db_obj)
            db.commit()

        if language_ids:
            for id in language_ids:
                obj_in = MeetingItemCreate(meeting_id=meeting_id, language_id=id)
                db_obj = MeetingLanguage(**obj_in.model_dump())
                db.add(db_obj)
            db.commit()

    def join_meeting(db: Session, user_id: int, meeting_id: int):
        # 이미 참가했는지 확인
        exists = db.query(MeetingUser).filter(
            MeetingUser.user_id == user_id, 
            MeetingUser.meeting_id == meeting_id
        ).first()
        
        if exists:
            raise HTTPException(status_code=400, detail="User already joined this meeting!")
        
        # Meeting에 User를 참가시킴
        meeting_user = MeetingUser(user_id=user_id, meeting_id=meeting_id)
        db.add(meeting_user)

        # Meeting의 current_participants 값을 증가 (만약 int 형태라면)
        meeting = db.query(Meeting).filter(id=meeting_id).first()
        if meeting:
            meeting.current_participants = str(int(meeting.current_participants) + 1)  # 만약 current_participants가 문자열 형태라면 int로 변환 후 처리
        else:
            raise HTTPException(status_code=400, detail="Meeting is not exists")
        
        db.commit()


meeting = CURDMeeting(Meeting)
