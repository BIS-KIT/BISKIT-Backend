import json
from typing import Any, Dict, Optional, Union, List
from datetime import datetime, timedelta
from firebase_admin import firestore

from sqlalchemy import desc, asc, func, extract, and_, or_, not_
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from crud.base import CRUDBase
from core.redis_driver import redis_driver
from core.config import settings
from log import log_error
import crud
from models.meeting import (
    Meeting,
    MeetingLanguage,
    MeetingTag,
    MeetingTopic,
    MeetingUser,
    Review,
)
from models.utility import Tag, Topic, Nationality, Language
from models.user import User, UserNationality
from schemas.meeting import (
    MeetingCreate,
    MeetingUpdate,
    MeetingUserCreate,
    MeetingIn,
    ReviewCreate,
    ReviewUpdate,
    MeetingUpdateIn,
    MeetingSummaryResponse,
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

    today = datetime.combine(datetime.today(), datetime.min.time())

    # 날짜 관련 필터
    if TimeFilterEnum.TODAY in time_filters:
        date_conditions.append(
            Meeting.meeting_time.between(today, today + timedelta(days=1))
        )

    if TimeFilterEnum.TOMORROW in time_filters:
        # 내일의 날짜만을 가져와서 datetime 객체로 변환
        tomorrow_start = datetime.combine(
            today.date() + timedelta(days=1), datetime.min.time()
        )
        # 다음날 00:00:00 시간
        next_day_start = tomorrow_start + timedelta(days=1)

        date_conditions.append(
            Meeting.meeting_time.between(tomorrow_start, next_day_start)
        )

    if TimeFilterEnum.THIS_WEEK in time_filters:
        start_of_week = datetime.combine(
            (today - timedelta(days=today.weekday())).date(), datetime.min.time()
        )
        end_of_week = start_of_week + timedelta(days=7)
        date_conditions.append(Meeting.meeting_time.between(start_of_week, end_of_week))

    if TimeFilterEnum.NEXT_WEEK in time_filters:
        start_of_next_week = datetime.combine(
            (today + timedelta(days=7 - today.weekday())).date(), datetime.min.time()
        )
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


class CURDMeeting(CRUDBase[Meeting, MeetingCreate, MeetingUpdateIn]):
    def create(self, db: Session, *, obj_in: MeetingCreate) -> Meeting:
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

        # meeting 생성되면 meeting 관련 캐시 무효
        cache_key_list = redis_driver.find_by_name_space(name_space="meetings")
        redis_driver.delete_keys(key_list=cache_key_list)
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
                # 기존 객체들 모두 삭제
                db.query(model).filter(model.meeting_id == meeting_id).delete()
                for id in ids:
                    obj_data = {"meeting_id": meeting_id, field_name: id}
                    db_obj = model(**obj_data)
                    db.add(db_obj)

        db.commit()

    def update_meeting(self, db: Session, meeting_id: int, obj_in: MeetingUpdate):
        meeting = self.get(db=db, id=meeting_id)

        data = obj_in.model_dump(exclude_none=True)
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

        try:
            update_meeting = super().update(
                db=db, db_obj=meeting, obj_in=MeetingUpdateIn(**data)
            )
            self.create_meeting_items(
                db, update_meeting.id, tag_ids, topic_ids, language_ids
            )
            if "name" in data and not settings.DEBUG:
                self.change_chat_room_name(name=data["name"], chat_id=meeting.chat_id)

        except:
            raise

        return update_meeting

    def change_chat_room_name(self, name: str, chat_id: str):
        firebase_db = firestore.client()
        doc = firebase_db.collection("ChatRoom").document(chat_id)

        doc.update({"title": name})
        return

    def filter_by_tags(self, query, tags_ids: Optional[List[int]]):
        return query.filter(Tag.id.in_(tags_ids))

    def filter_by_topics(self, query, db: Session, topics_ids: Optional[List[int]]):
        etc_tag = db.query(Topic).filter(Topic.kr_name == "기타").first()
        if etc_tag and etc_tag.id in topics_ids:
            return query.filter(or_(Topic.is_custom == True, Topic.id.in_(topics_ids)))
        return query.filter(Topic.id.in_(topics_ids))

    def filter_by_time(self, query, time_filters: Optional[List[TimeFilterEnum]]):
        if time_filters:
            conditions = check_time_conditions(time_filters)
            return query.filter(conditions)
        else:
            return query

    def filter_by_search_word(self, query, search_word: str):
        # 검색어를 풀텍스트 쿼리 형식으로 변환
        search_query = func.to_tsquery(f"{search_word}:*")

        # 텍스트 데이터를 검색 가능한 구조로 변환
        name_vector = func.to_tsvector("simple", Meeting.name)
        description_vector = func.to_tsvector("simple", Meeting.description)
        language_kr_vector = func.to_tsvector("simple", Language.kr_name)
        language_en_vector = func.to_tsvector("simple", Language.en_name)

        # 텍스트 검색 벡터와 쿼리를 비교
        search_filter = (
            name_vector.op("@@")(search_query)
            | description_vector.op("@@")(search_query)
            | Meeting.meeting_languages.any(
                MeetingLanguage.language.has(
                    language_kr_vector.op("@@")(search_query)
                    | language_en_vector.op("@@")(search_query)
                )
            )
        )

        return_query = query.filter(search_filter)
        return return_query

    def filter_by_nationality(self, query, nationality_name: str):
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

    def filter_by_ban(self, db: Session, query, user_id: int):
        user_university = crud.user.get_university(db=db, user_id=user_id)
        university_id = user_university.university_id

        target_list = crud.ban.get_target_ids(db=db, user_id=user_id)

        if target_list:
            query = query.filter(
                Meeting.university_id == university_id,
                not_(Meeting.creator_id.in_(target_list)),
            )
        else:
            query = query.filter(Meeting.university_id == university_id)

        return query

    def get_meetings_by_university(
        self, db: Session, user_id: int, skip: int, limit: int
    ):
        university = crud.utility.get_university_by_user(db=db, user_id=user_id)
        if not university:
            raise HTTPException(status_code=400, detail="University is not exists")
        query = db.query(Meeting).filter(Meeting.university_id == university.id)
        query = self.filter_by_ban(db=db, query=query, user_id=user_id)
        total_count = query.count()
        return query.offset(skip).limit(limit).all(), total_count

    def get_multi(
        self,
        db: Session,
        order_by: str,
        skip: int,
        limit: int,
        creator_nationality: Optional[str],
        user_id: int,
        is_public: bool,
        is_active: bool = True,
        tags_ids: Optional[List[int]] = None,
        topics_ids: Optional[List[int]] = None,
        time_filters: Optional[List[str]] = None,
        is_count_only: Optional[bool] = False,
        search_word: str = None,
    ) -> List[Meeting]:
        # query = db.query(Meeting).filter(Meeting.is_active == is_active)
        query = db.query(Meeting).filter(Meeting.is_public == is_public)
        cache_key = redis_driver.generate_cache_key(
            name_space="meetings",
            order_by=order_by,
            skip=skip,
            limit=limit,
            creator_nationality=creator_nationality,
            user_id=user_id,
            is_public=is_public,
            tags_ids=tags_ids,
            topics_ids=topics_ids,
            time_filters=time_filters,
            is_count_only=is_count_only,
            search_word=search_word,
        )

        if redis_driver.is_cached(key=cache_key):
            cached_data = redis_driver.get_value(key=cache_key)
            return_query = query.filter(Meeting.id.in_(cached_data)).all()

            return_query.sort(key=lambda x: cached_data.index(x.id))

            return return_query, len(return_query)

        if user_id and not is_public:
            query = self.filter_by_ban(db, query, user_id)

        if creator_nationality:
            query = self.filter_by_nationality(query, creator_nationality)

        if time_filters:
            query = self.filter_by_time(query, time_filters)

        if tags_ids:
            query = query.join(MeetingTag).join(Tag)
            query = self.filter_by_tags(query, tags_ids)

        if topics_ids:
            query = query.join(MeetingTopic).join(Topic)
            query = self.filter_by_topics(query=query, topics_ids=topics_ids, db=db)

        if search_word:
            query = self.filter_by_search_word(query=query, search_word=search_word)

        # order by 전에 count
        total_count_query = query.distinct()
        total_count = total_count_query.count()

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

            # 참여 인원 적은 순
            participants_difference = func.abs(
                Meeting.max_participants - Meeting.current_participants
            )

            query = query.order_by(
                participants_difference.asc(), time_difference_seconds.asc()
            )
        else:
            query = query.order_by(desc(Meeting.created_time))

        if is_count_only:
            return [], total_count

        # n+1 해결 위한 eager loading
        meeting_list = (
            query.options(
                joinedload(Meeting.meeting_tags).joinedload(MeetingTag.tag),
                joinedload(Meeting.meeting_topics).joinedload(MeetingTopic.topic),
                joinedload(Meeting.creator).joinedload(User.profile),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        meeting_ids = [meeting.id for meeting in meeting_list]

        redis_driver.set_value(
            key=cache_key,
            value=json.dumps(meeting_ids),
        )

        return meeting_list, total_count

    def get_requests(
        self, db: Session, meeting_id: int, skip: int, limit: int
    ) -> List[MeetingUser]:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

        if not meeting:
            raise HTTPException(status_code=400, detail="Meeting is not exists")

        query = db.query(MeetingUser).filter(MeetingUser.meeting_id == meeting_id)
        total_count = query.count()
        return query.offset(skip).limit(limit).all(), total_count

    def join_request_approve(self, db: Session, obj_id: int):

        join_request = (
            db.query(MeetingUser)
            .filter(
                MeetingUser.id == obj_id,
                MeetingUser.status == ReultStatusEnum.PENDING,
            )
            .first()
        )

        if not join_request:
            raise HTTPException(status_code=400, detail="Join Request not found")

        join_request.status = ReultStatusEnum.APPROVE.value

        meeting = (
            db.query(Meeting).filter(Meeting.id == join_request.meeting_id).first()
        )

        if meeting.current_participants >= meeting.max_participants:
            raise HTTPException(status_code=404, detail="It's full of people.")

        return join_request

    def join_request_reject(self, db: Session, obj_id: int):
        join_request = db.query(MeetingUser).filter(MeetingUser.id == obj_id).delete()
        db.commit()
        return join_request

    def join_request(self, db: Session, obj_in: MeetingUserCreate):
        user_id = obj_in.user_id
        meeting_id = obj_in.meeting_id

        # TODO : TEST 중에만 잠시 제외
        check_student_verifiy = crud.profile.check_student_card_verifiy(
            db=db, user_id=user_id
        )

        try:
            # 이미 참가했는지 확인
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
            log_error(e)
            raise HTTPException(status_code=500, detail=str(e))
        return meeting_user

    def check_meeting_request_status(self, db: Session, meeting_id: int, user_id: int):
        meeting_user = (
            db.query(MeetingUser)
            .filter(
                MeetingUser.meeting_id == meeting_id, MeetingUser.user_id == user_id
            )
            .first()
        )
        return meeting_user

    def exit_meeting(self, db: Session, meeting_id: int, user_id: int):
        # 해당 모임 참가자 확인
        meeting_user = (
            db.query(MeetingUser)
            .filter(
                MeetingUser.meeting_id == meeting_id, MeetingUser.user_id == user_id
            )
            .first()
        )

        if not meeting_user:
            raise HTTPException(
                status_code=400, detail="User not joined in this meeting"
            )

        # 모임 참가자 목록에서 제거
        db.delete(meeting_user)
        db.commit()

        return {"detail": "Successfully left the meeting"}

    def get_all_active_meeting(self, db: Session):
        all_meetings = db.query(Meeting).filter(Meeting.is_active == True).all()
        return all_meetings

    def get_meeting_wieh_chat(self, db: Session, chad_id: str):
        meeting = db.query(Meeting).filter(Meeting.chat_id == chad_id).first()
        return meeting

    def get_meeting_with_hour(self, db: Session, current_time: datetime.time) -> List:
        one_hour_later = current_time + timedelta(hours=1)

        meetings = (
            db.query(Meeting)
            .filter(
                Meeting.meeting_time >= one_hour_later,
                Meeting.meeting_time < one_hour_later + timedelta(minutes=1),
            )
            .all()
        )

        meeting_id_list = [meeting.id for meeting in meetings]
        return meeting_id_list


class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewUpdate]):
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, user_id: int = None
    ) -> List[Review]:
        query = db.query(self.model)
        total_count = query.count()
        if user_id:
            query = query.filter(self.model.creator_id == user_id)
            total_count = query.count()
            return query.offset(skip).limit(limit).all(), total_count
        else:
            return query.offset(skip).limit(limit).all(), total_count


meeting = CURDMeeting(Meeting)
review = CRUDReview(Review)
