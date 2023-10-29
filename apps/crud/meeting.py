from typing import Any, Dict, Optional, Union, List

from sqlalchemy import desc, asc, func, extract
from sqlalchemy.orm import Session
from fastapi import HTTPException

from crud.base import CRUDBase
import crud
from models.meeting import (
    Meeting,
    MeetingLanguage,
    MeetingTag,
    MeetingTopic,
    MeetingUser,
)
from schemas.meeting import (
    MeetingCreateUpdate,
    MeetingItemCreate,
    MeetingUserCreate,
    MeetingIn,
    MeetingOrderingEnum,
)


class CURDMeeting(CRUDBase[Meeting, MeetingCreateUpdate, MeetingCreateUpdate]):
    def create(self, db: Session, *, obj_in: MeetingCreateUpdate) -> Meeting:
        data = obj_in.model_dump()
        tag_ids = data.pop("tag_ids", [])
        topic_ids = data.pop("topic_ids", [])
        language_ids = data.pop("language_ids", [])

        custom_tags = data.pop("custom_tags", [])
        custom_topics = data.pop("custom_topics", [])

        if custom_tags:
            for name in custom_tags:
                new_tag = crud.utility.create_tag(db=db, name=name)
                tag_ids.append(new_tag.id)

        if custom_topics:
            for name in custom_topics:
                new_topic = crud.utility.create_topic(db=db, name=name)
                topic_ids.append(new_topic.id)

        user_nationalities = crud.user.get_nationality_by_user_id(
            db=db, user_id=data["creator_id"]
        )
        codes = [un.nationality.code for un in user_nationalities]
        if codes:
            if "kr" in codes:
                data.setdefault("korean_count", 0)
                data["korean_count"] += 1
            else:
                data.setdefault("foreign_count", 0)
                data["foreign_count"] += 1

        new_meeting = super().create(db=db, obj_in=MeetingIn(**data))
        self.create_meeting_items(db, new_meeting.id, tag_ids, topic_ids, language_ids)
        return new_meeting

    def create_meeting_items(
        self,
        db: Session,
        meeting_id: int,
        tags_ids: List[int],
        topic_ids: List[int],
        language_ids: List[int],
    ):
        tags_ids = tags_ids or []
        topic_ids = topic_ids or []
        language_ids = language_ids or []

        items = [
            (tags_ids, MeetingTag, "tag_id"),
            (topic_ids, MeetingTopic, "topic_id"),
            (language_ids, MeetingLanguage, "language_id"),
        ]

        for ids, model, field_name in items:
            if ids:
                for id in ids:
                    obj_data = {"meeting_id": meeting_id, field_name: id}
                    db_obj = model(**obj_data)
                    db.add(db_obj)

        db.commit()

    def get_multi(
        self,
        db: Session,
        order_by: str,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Meeting]:
        query = db.query(Meeting).filter(Meeting.is_active == is_active)

        if order_by == MeetingOrderingEnum.CREATED_TIME:
            query = query.order_by(desc(Meeting.created_time))
        elif order_by == MeetingOrderingEnum.MEETING_TIME:
            query = query.order_by(asc(Meeting.meeting_time))
        # 현재 시간과 meeting_time의 차이를 계산하여 정렬
        elif order_by == MeetingOrderingEnum.DEADLINE_SOON:
            # 현재 시간 이후의 모임만 선택
            query = query.filter(Meeting.meeting_time > func.now())

            # meeting_time과 now() 사이의 시간 차이를 초로 계산
            time_difference_seconds = extract(
                "epoch", Meeting.meeting_time - func.now()
            )
            query = query.order_by(time_difference_seconds)
        else:
            # 기본 정렬은 CREATED_TIME 기준으로
            query = query.order_by(desc(Meeting.created_time))

        return query.offset(skip).limit(limit).all()

    def join_meeting(db: Session, obj_in: MeetingUserCreate):
        # 이미 참가했는지 확인
        user_id = obj_in.user_id
        meeting_id = obj_in.meeting_id
        exists = (
            db.query(MeetingUser)
            .filter(
                MeetingUser.user_id == user_id, MeetingUser.meeting_id == meeting_id
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=400, detail="User already joined this meeting!"
            )

        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

        if not meeting:
            raise HTTPException(status_code=400, detail="Meeting is not exists")

        # 참여 가능한 인원 수 확인
        if meeting.current_participants >= meeting.max_participants:
            raise HTTPException(status_code=400, detail="The meeting is already full!")

        # Meeting에 User를 참가시킴
        meeting_user = MeetingUser(user_id=user_id, meeting_id=meeting_id)
        db.add(meeting_user)

        user_nationalities = crud.user.get_nationality_by_user_id(
            db=db, user_id=user_id
        )
        codes = [un.nationality.code for un in user_nationalities]
        meeting.current_participants = meeting.current_participants + 1
        if codes:
            if "kr" in codes:
                meeting.korean_count = meeting.korean_count + 1
            else:
                meeting.foreign_count = meeting.foreign_count + 1

        db.commit()


meeting = CURDMeeting(Meeting)
