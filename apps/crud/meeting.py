from typing import Any, Dict, Optional, Union, List
from datetime import datetime, timedelta

from sqlalchemy import desc, asc, func, extract, and_, or_
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
from models.utility import Tag, Topic
from schemas.meeting import (
    MeetingCreateUpdate,
    MeetingItemCreate,
    MeetingUserCreate,
    MeetingIn,
    MeetingOrderingEnum,
    TimeFilterEnum,
)


def check_time_conditions(time_filters: TimeFilterEnum):
    time_conditions = []

    today = datetime.today()

    if TimeFilterEnum.TODAY in time_filters:
        time_conditions.append(
            Meeting.meeting_time.between(today, today + timedelta(days=1))
        )

    if TimeFilterEnum.TOMORROW in time_filters:
        tomorrow = today + timedelta(days=1)
        time_conditions.append(
            Meeting.meeting_time.between(tomorrow, tomorrow + timedelta(days=1))
        )

    if TimeFilterEnum.THIS_WEEK in time_filters:
        # Assuming the week starts on Monday
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=7)
        time_conditions.append(Meeting.meeting_time.between(start_of_week, end_of_week))

    if TimeFilterEnum.NEXT_WEEK in time_filters:
        # Assuming the week starts on Monday
        start_of_next_week = today + timedelta(days=7 - today.weekday())
        end_of_next_week = start_of_next_week + timedelta(days=7)
        time_conditions.append(
            Meeting.meeting_time.between(start_of_next_week, end_of_next_week)
        )

    # 요일별 필터링
    if TimeFilterEnum.MONDAY in time_filters:
        time_conditions.append(extract("dow", Meeting.meeting_time) == 1)  # 1은 월요일

    if TimeFilterEnum.TUESDAY in time_filters:
        time_conditions.append(extract("dow", Meeting.meeting_time) == 2)  # 2는 화요일

    if TimeFilterEnum.WEDNESDAY in time_filters:
        time_conditions.append(extract("dow", Meeting.meeting_time) == 3)  # 3은 수요일

    if TimeFilterEnum.THURSDAY in time_filters:
        time_conditions.append(extract("dow", Meeting.meeting_time) == 4)  # 4는 목요일

    if TimeFilterEnum.FRIDAY in time_filters:
        time_conditions.append(extract("dow", Meeting.meeting_time) == 5)  # 5는 금요일

    if TimeFilterEnum.SATURDAY in time_filters:
        time_conditions.append(extract("dow", Meeting.meeting_time) == 6)  # 6은 토요일

    if TimeFilterEnum.SUNDAY in time_filters:
        time_conditions.append(extract("dow", Meeting.meeting_time) == 0)  # 0은 일요일

    # Morning, Afternoon, Evening 조건 추가
    if TimeFilterEnum.MORNING in time_filters:
        time_conditions.append(extract("hour", Meeting.meeting_time) < 12)

    if TimeFilterEnum.AFTERNOON in time_filters:
        time_conditions.append(
            and_(
                extract("hour", Meeting.meeting_time) >= 12,
                extract("hour", Meeting.meeting_time) < 18,
            )
        )

    if TimeFilterEnum.EVENING in time_filters:
        time_conditions.append(extract("hour", Meeting.meeting_time) >= 18)
    return time_conditions


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

    def filter_by_tags(self, query, tags_ids: Optional[List[int]]):
        return query.join(MeetingTag).join(Tag).filter(Tag.id.in_(tags_ids))

    def filter_by_topics(self, query, topics_ids: Optional[List[int]]):
        return query.join(MeetingTopic).join(Topic).filter(Topic.id.in_(topics_ids))

    def filter_by_time(self, query, time_filters: Optional[List[TimeFilterEnum]]):
        time_conditions = check_time_conditions(time_filters)
        return query.filter(and_(*time_conditions))

    def get_multi(
        self,
        db: Session,
        order_by: str,
        skip: int,
        limit: int,
        is_active: bool = True,
        tags_ids: Optional[List[int]] = None,
        topics_ids: Optional[List[int]] = None,
        time_filters: Optional[List[str]] = None,
    ) -> List[Meeting]:
        query = db.query(Meeting).filter(Meeting.is_active == is_active)

        if tags_ids:
            query = self.filter_by_tags(query, tags_ids)

        if topics_ids:
            query = self.filter_by_topics(query, topics_ids)

        if time_filters:
            query = self.filter_by_time(query, time_filters)

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
            query = query.order_by(desc(Meeting.created_time))

        total_count = query.count()

        return query.offset(skip).limit(limit).all(), total_count

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
