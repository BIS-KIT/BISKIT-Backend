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
    Review,
)
from models.utility import Tag, Topic, Nationality
from models.user import User, UserNationality
from schemas.meeting import (
    MeetingCreateUpdate,
    MeetingItemCreate,
    MeetingUserCreate,
    MeetingIn,
    ReviewCreate,
    ReviewUpdate,
    ReviwPhotoCreate,
)
from schemas.enum import (
    MeetingOrderingEnum,
    TimeFilterEnum,
    ReultStatusEnum,
    CreatorNationalityEnum,
)


def check_time_conditions(time_filters: List[TimeFilterEnum]):
    date_conditions = []
    day_of_week_conditions = []
    time_of_day_conditions = []

    today = datetime.today()

    # 날짜 관련 필터
    if TimeFilterEnum.TODAY in time_filters:
        date_conditions.append(
            Meeting.meeting_time.between(today, today + timedelta(days=1))
        )

    if TimeFilterEnum.TOMORROW in time_filters:
        tomorrow = today + timedelta(days=1)
        date_conditions.append(
            Meeting.meeting_time.between(tomorrow, tomorrow + timedelta(days=1))
        )

    if TimeFilterEnum.THIS_WEEK in time_filters:
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=7)
        date_conditions.append(Meeting.meeting_time.between(start_of_week, end_of_week))

    if TimeFilterEnum.NEXT_WEEK in time_filters:
        start_of_next_week = today + timedelta(days=7 - today.weekday())
        end_of_next_week = start_of_next_week + timedelta(days=7)
        date_conditions.append(
            Meeting.meeting_time.between(start_of_next_week, end_of_next_week)
        )

    # 요일별 필터링
    for dow_enum, dow_int in [
        (TimeFilterEnum.MONDAY, 1),
        (TimeFilterEnum.TUESDAY, 2),
        (TimeFilterEnum.WEDNESDAY, 3),
        (TimeFilterEnum.THURSDAY, 4),
        (TimeFilterEnum.FRIDAY, 5),
        (TimeFilterEnum.SATURDAY, 6),
        (TimeFilterEnum.SUNDAY, 0),
    ]:
        if dow_enum in time_filters:
            day_of_week_conditions.append(
                extract("dow", Meeting.meeting_time) == dow_int
            )

    # 시간대별 필터
    if TimeFilterEnum.MORNING in time_filters:
        time_of_day_conditions.append(extract("hour", Meeting.meeting_time) < 12)

    if TimeFilterEnum.AFTERNOON in time_filters:
        time_of_day_conditions.append(
            and_(
                extract("hour", Meeting.meeting_time) >= 12,
                extract("hour", Meeting.meeting_time) < 18,
            )
        )

    if TimeFilterEnum.EVENING in time_filters:
        time_of_day_conditions.append(extract("hour", Meeting.meeting_time) >= 18)

    # 각 필터 카테고리 내부의 조건들을 or_ 로 결합합니다.
    combined_date_conditions = or_(*date_conditions) if date_conditions else None
    combined_day_of_week_conditions = (
        or_(*day_of_week_conditions) if day_of_week_conditions else None
    )
    combined_time_of_day_conditions = (
        or_(*time_of_day_conditions) if time_of_day_conditions else None
    )

    # 최종 조건 리스트를 생성합니다.
    final_conditions = [
        cond
        for cond in [
            combined_date_conditions,
            combined_day_of_week_conditions,
            combined_time_of_day_conditions,
        ]
        if cond is not None
    ]

    # 카테고리 간의 조건들은 and_ 로 결합하여 반환합니다.
    if final_conditions:
        return and_(*final_conditions)
    else:
        # If there are no conditions, return a truthy condition
        return True


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

        user_university = crud.user.get_university(db=db, user_id=data["creator_id"])
        data["university_id"] = (
            user_university.university_id if user_university else None
        )

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
        if time_filters:
            conditions = check_time_conditions(time_filters)
            return query.filter(conditions)
        else:
            return query

    def filter_by_nationality(self, query, nationality_name: str):
        print(nationality_name)
        if nationality_name == CreatorNationalityEnum.KOREAN.value:
            return (
                query.join(Meeting.creator)
                .join(User.user_nationality)
                .join(UserNationality.nationality)
                .filter(Nationality.code == "kr")
            )
        elif nationality_name == CreatorNationalityEnum.FOREIGNER.value:
            return (
                query.join(Meeting.creator)
                .join(User.user_nationality)
                .join(UserNationality.nationality)
                .filter(Nationality.code != "kr")
            )
        else:
            return query

    def get_multi(
        self,
        db: Session,
        order_by: str,
        skip: int,
        limit: int,
        creator_nationality: Optional[str],
        is_active: bool = True,
        tags_ids: Optional[List[int]] = None,
        topics_ids: Optional[List[int]] = None,
        time_filters: Optional[List[str]] = None,
        is_count_only: Optional[bool] = False,
    ) -> List[Meeting]:
        query = db.query(Meeting).filter(Meeting.is_active == is_active)

        if creator_nationality:
            query = self.filter_by_nationality(query, creator_nationality)

        if time_filters:
            query = self.filter_by_time(query, time_filters)

        if tags_ids:
            query = self.filter_by_tags(query, tags_ids)

        if topics_ids:
            query = self.filter_by_topics(query, topics_ids)

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
        if is_count_only:
            return [], total_count

        return query.offset(skip).limit(limit).all(), total_count

    def get_requests(self, db: Session, meeting_id: int) -> List[MeetingUser]:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

        if not meeting:
            raise HTTPException(status_code=400, detail="Meeting is not exists")
        return db.query(MeetingUser).filter(MeetingUser.meeting_id == meeting_id).all()

    def join_request_approve(self, db: Session, obj_id: int):
        join_request = db.query(MeetingUser).filter(MeetingUser.id == obj_id).first()

        if not join_request:
            raise HTTPException(status_code=400, detail="Join Request not found")

        join_request.status = ReultStatusEnum.APPROVE.value

        user_nationalities = crud.user.get_nationality_by_user_id(
            db=db, user_id=join_request.user_id
        )

        meeting = (
            db.query(Meeting).filter(Meeting.id == join_request.meeting_id).first()
        )

        codes = [un.nationality.code for un in user_nationalities]
        meeting.current_participants = meeting.current_participants + 1
        if codes:
            if "kr" in codes:
                meeting.korean_count = meeting.korean_count + 1
            else:
                meeting.foreign_count = meeting.foreign_count + 1
        db.commit()
        return

    def join_request_reject(self, db: Session, obj_id: int):
        join_request = db.query(MeetingUser).filter(MeetingUser.id == obj_id).first()

        if not join_request:
            raise HTTPException(status_code=400, detail="Join Request not found")

        join_request.status = ReultStatusEnum.REJECTED.value
        db.commit()
        return

    def join_request(self, db: Session, obj_in: MeetingUserCreate):
        # 이미 참가했는지 확인
        user_id = obj_in.user_id
        meeting_id = obj_in.meeting_id

        try:
            # atomic 유지하기 위해 transtaction 시작
            db.begin()

            meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

            if not meeting:
                raise HTTPException(status_code=400, detail="Meeting is not exists")

            # 참여 가능한 인원 수 확인
            if meeting.current_participants >= meeting.max_participants:
                raise HTTPException(
                    status_code=400, detail="The meeting is already full!"
                )

            existing_request = (
                db.query(MeetingUser)
                .filter(
                    MeetingUser.user_id == user_id,
                    MeetingUser.meeting_id == meeting_id,
                    MeetingUser.status.in_(
                        [ReultStatusEnum.PENDING.value, ReultStatusEnum.APPROVE.value]
                    ),
                )
                .first()
            )

            if existing_request:
                raise HTTPException(
                    status_code=400, detail="User already joined this meeting!"
                )

            meeting_user = MeetingUser(
                user_id=user_id,
                meeting_id=meeting_id,
                status=ReultStatusEnum.PENDING.value,
            )

            db.add(meeting_user)
            db.commit()
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        return meeting_user


class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewUpdate]):
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, user_id: int = None
    ) -> List[Review]:
        if user_id:
            return (
                db.query(self.model)
                .filter(self.model.creator_id == user_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        else:
            return db.query(self.model).offset(skip).limit(limit).all()


meeting = CURDMeeting(Meeting)
review = CRUDReview(Review)
