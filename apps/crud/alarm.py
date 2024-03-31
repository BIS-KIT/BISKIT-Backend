from firebase_admin import messaging

from firebase_admin import firestore
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from firebase_admin.exceptions import InvalidArgumentError
from typing import List, Dict

import crud
from crud.base import CRUDBase
from schemas.enum import LogTypeEnum
from models import alarm as alarm_model
from schemas import alarm as alarm_schema
from core.config import settings
from log import log_error


def send_fcm_notification(
    title: str,
    body: str,
    user_tokens: Dict[int, str],
    db: Session = None,
    data: Dict[str, str] = None,
):
    """
    FCM을 통해 푸시 알림을 전송하는 함수

    :param title: 알림의 제목
    :param body: 알림의 내용
    :param user_tokens: 대상 장치의 FCM 토큰과 사용자 ID를 담은 딕셔너리
    :param data: 알림과 함께 보낼 추가 데이터
    """
    for user_id, fcm_token in user_tokens.items():
        try:

            # 알람보내기
            messages = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data,
                token=fcm_token,
            )
            response = messaging.send(messages)

            # 알람 객체 생성
            obj_in = alarm_schema.AlarmCreate(
                title=title, content=body, user_id=user_id
            )
            created_alarm = alarm.create(db=db, obj_in=obj_in)

        except InvalidArgumentError as e:
            # FCM 토큰 관련 오류 처리
            log_error(e, type=LogTypeEnum.ALARM.value)
            continue

        except SQLAlchemyError as e:
            # DB 관련 오류 처리
            log_error(e, type=LogTypeEnum.ALARM.value)
            continue

        except Exception as e:
            log_error(e, type=LogTypeEnum.ALARM.value)
            continue

    return None


class Alarm(
    CRUDBase[alarm_model.Alarm, alarm_schema.AlarmCreate, alarm_schema.AlarmCreate]
):
    def read_alarm(self, db: Session, alarm_id):
        alarm_obj = (
            db.query(alarm_model.Alarm).filter(alarm_model.Alarm.id == alarm_id).first()
        )
        alarm_obj.is_read = True
        db.commit()
        return alarm_obj

    def create_meeting_request(self, db: Session, user_id: int, meeting_id: int):
        """
        모임 참가 신청 알람 to 모임 생성자
        """
        meeting = crud.meeting.get(db=db, id=meeting_id)
        requester = crud.user.get(db=db, id=user_id)
        creator_id = meeting.creator_id

        meeting_name = meeting.name
        target_fcm_token = crud.user.get_user_fcm_token(db=db, user_id=creator_id)
        requester_nick_name = requester.nick_name
        title = "모임 신청"
        body = f"{requester_nick_name}님이 {meeting_name} 모임에 신청했어요."

        user_token = {user_id: target_fcm_token}
        icon_url = settings.S3_URL + "/default_icon/Thumbnail_Icon_Notify.svg"
        data = {
            "meeting_id": str(meeting_id),
            "icon_url": str(icon_url),
            "is_main_alarm": "True",
            "is_sub_alarm": "False",
        }
        return send_fcm_notification(
            db=db,
            title=title,
            body=body,
            user_tokens=user_token,
            data=data,
        )

    def cancle_meeting(
        self, db: Session, meeting_name: str, user_tokens: Dict[int, str]
    ):
        """
        모임 취소 및 삭제 알림 to 모임 신청자
        """
        title = "모임 취소"
        body = f"{meeting_name} 모임이 취소되었어요."
        icon_url = settings.S3_URL + "/default_icon/Thumbnail_Icon_Notify.svg"

        data = {
            "icon_url": str(icon_url),
            "is_main_alarm": "True",
            "is_sub_alarm": "False",
        }

        return send_fcm_notification(
            db=db,
            title=title,
            body=body,
            user_tokens=user_tokens,
            data=data,
        )

    def exit_meeting(self, db: Session, user_id: int, meeting_id: int):
        """
        모임 탈퇴 알람 to 모임 생성자
        """
        meeting = crud.meeting.get(db=db, id=meeting_id)
        requester = crud.user.get(db=db, id=user_id)
        creator_id = meeting.creator_id

        meeting_name = meeting.name
        target_fcm_token = crud.user.get_user_fcm_token(db=db, user_id=creator_id)
        requester_nick_name = requester.nick_name

        title = "모임 탈퇴"
        body = f"{requester_nick_name}님이 {meeting_name} 모임에서 나갔어요."

        user_token = {creator_id: target_fcm_token}
        icon_url = settings.S3_URL + "/default_icon/Thumbnail_Icon_Notify.svg"
        data = {
            "meeting_id": str(meeting_id),
            "icon_url": str(icon_url),
            "is_main_alarm": "True",
            "is_sub_alarm": "False",
        }
        return send_fcm_notification(
            db=db,
            title=title,
            body=body,
            user_tokens=user_token,
            data=data,
        )

    def meeting_request_approve(self, db: Session, user_id: int, meeting_id: int):
        """
        모임 승인 알람 to 모임 신청자
        """
        meeting = crud.meeting.get(db=db, id=meeting_id)

        meeting_name = meeting.name
        target_fcm_token = crud.user.get_user_fcm_token(db=db, user_id=user_id)

        title = "모임 승인"
        body = f"{meeting_name} 모임에 승인되었어요."

        user_token = {user_id: target_fcm_token}
        icon_url = settings.S3_URL + "/default_icon/Thumbnail_Icon_Notify.svg"
        data = {
            "meeting_id": str(meeting_id),
            "icon_url": str(icon_url),
            "is_main_alarm": "True",
            "is_sub_alarm": "False",
        }
        return send_fcm_notification(
            db=db,
            title=title,
            body=body,
            user_tokens=user_token,
            data=data,
        )

    def meeting_request_reject(self, db: Session, user_id: int, meeting_id: int):
        meeting = crud.meeting.get(db=db, id=meeting_id)

        meeting_name = meeting.name
        target_fcm_token = crud.user.get_user_fcm_token(db=db, user_id=user_id)

        title = "모임 거절"
        body = f"{meeting_name} 모임에 거절되었어요."

        user_token = {user_id: target_fcm_token}
        icon_url = settings.S3_URL + "/default_icon/Thumbnail_Icon_Notify.svg"
        data = {
            "meeting_id": str(meeting_id),
            "icon_url": str(icon_url),
            "is_main_alarm": "True",
            "is_sub_alarm": "False",
        }
        return send_fcm_notification(
            db=db,
            title=title,
            body=body,
            user_tokens=user_token,
            data=data,
        )

    def notice_alarm(self, db: Session, title: str, content: str, notice_id: int):
        users = crud.user.get_all_users(db=db)

        user_tokens = {user.id: user.fcm_token for user in users}
        icon_url = settings.S3_URL + "/default_icon/Thumbnail_notice_Icon.svg"
        data = {
            "notice_id": str(notice_id),
            "icon_url": str(icon_url),
            "is_main_alarm": "False",
            "is_sub_alarm": "True",
        }

        try:
            send_fcm_notification(
                title=title,
                body=content,
                user_tokens=user_tokens,
                db=db,
                data=data,
            )
        except Exception as e:
            log_error(e)
            return False
        return True

    def report_alarm(self, db: Session, target_id: int):
        target_fcm_token = crud.user.get_user_fcm_token(db=db, user_id=target_id)
        get_all_report = crud.report.get_by_user_id(db=db, user_id=target_id)

        title = "경고"
        body = (
            f"서비스 이용규정 위반으로 경고가 {len(get_all_report)}회 누적되었습니다."
        )

        user_tokens = {target_id: target_fcm_token}
        icon_url = settings.S3_URL + "/default_icon/Thumbnail_reprot_icon.svg"
        data = {
            "reporter_id": str(target_id),
            "icon_url": str(icon_url),
            "is_main_alarm": "False",
            "is_sub_alarm": "True",
        }
        return send_fcm_notification(
            db=db,
            title=title,
            body=body,
            user_tokens=user_tokens,
            data=data,
        )

    def chat_alarm(self, db: Session, chat_id: str, content: str):
        # Firebase Realtime Database에서 채팅방 데이터 읽기
        firebase_db = firestore.client()
        # 특정 문서 참조
        doc_ref = firebase_db.collection("ChatRoom").document(chat_id)
        doc = doc_ref.get()

        # 문서 존재 여부 확인 및 필요한 필드 추출
        if not doc.exists:
            raise ValueError("Chat Not Found")

        meeting = crud.meeting.get_meeting_wieh_chat(db=db, chad_id=chat_id)
        creator_fcm = crud.user.get_user_fcm_token(db=db, user_id=meeting.creator_id)
        meeting_name = meeting.name

        data = {
            "chat_id": str(chat_id),
            "is_main_alarm": "True",
            "is_sub_alarm": "False",
        }

        # 현재 채팅창에 활성화 되어 있는 유저 제외
        chat_users_dict = crud.user.read_all_chat_users(db=db, chat_id=chat_id)

        # 채팅방 생성자의 FCM 토큰 추가
        if creator_fcm:
            chat_users_dict[meeting.creator_id] = creator_fcm

        doc_data = doc.to_dict()
        connecting_users = doc_data.get("connectingUsers", [])
        # remaining_users = {
        #     user_id: fcm_token
        #     for user_id, fcm_token in chat_users_dict.items()
        #     if user_id not in connecting_users
        # }

        remaining_users_fcm = [
            fcm_token
            for user_id, fcm_token in chat_users_dict.items()
            if user_id not in connecting_users
        ]

        send_fcm_notification(
            title=meeting_name, body=content, fcm_tokens=remaining_users_fcm, data=data
        )

        # TODO : 각 유저의 차단 유저 제외
        return True

    def get_multi_with_user_id(
        self, db: Session, user_id: int, skip: int = 0, limit: int = 10
    ) -> List[alarm_model.Alarm]:
        query = (
            db.query(alarm_model.Alarm)
            .filter(alarm_model.Alarm.user_id == user_id)
            .order_by(alarm_model.Alarm.is_read, alarm_model.Alarm.created_time.desc())
        )
        total_count = query.count()
        return query.offset(skip).limit(limit).all(), total_count

    def delete_alarms(self, db: Session, user_id: int):
        query = (
            db.query(alarm_model.Alarm)
            .filter(
                alarm_model.Alarm.user_id == user_id, alarm_model.Alarm.is_read == True
            )
            .delete()
        )
        db.commit()
        return None


alarm = Alarm(alarm_model.Alarm)
