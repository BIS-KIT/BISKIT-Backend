from firebase_admin import messaging

from firebase_admin import firestore
from sqlalchemy.orm import Session
from firebase_admin.exceptions import InvalidArgumentError
from typing import List, Dict

import crud
from schemas.enum import LogTypeEnum
from core.config import settings
from log import log_error


def send_fcm_notification(
    title: str, body: str, fcm_tokens: List[str], data: Dict[str, str] = None
):
    """
    FCM을 통해 푸시 알림을 전송하는 함수
    :param title: 알림의 제목
    :param body: 알림의 내용
    :param fcm_token: 대상 장치의 FCM 토큰
    """
    try:
        messages = [
            messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data,
                token=token,
            )
            for token in fcm_tokens
        ]
        response = messaging.send_all(messages)
        return response
    except InvalidArgumentError as e:
        # FCM 토큰 관련 오류 처리
        log_error(e, type=LogTypeEnum.ALARM.value)
        pass
    except Exception as e:
        log_error(e, type=LogTypeEnum.ALARM.value)
        raise e


class Alarm:
    def create_meeting_request(self, db: Session, user_id: int, meeting_id: int):
        meeting = crud.meeting.get(db=db, id=meeting_id)
        requester = crud.user.get(db=db, id=user_id)

        meeting_name = meeting.name
        target_fcm_token = crud.user.get_user_fcm_token(
            db=db, user_id=meeting.creator_id
        )
        requester_nick_name = requester.nick_name
        title = "모임 신청"
        body = f"{requester_nick_name}님이 {meeting_name} 모임에 신청했어요."

        icon_url = settings.S3_URL + "/default_icon/Thumbnail_Icon_Notify.svg"
        data = {"meeting_id": str(meeting_id), "icon_url": str(icon_url)}
        return send_fcm_notification(title, body, [target_fcm_token], data)

    def exit_meeting(self, db: Session, user_id: int, meeting_id: int):
        meeting = crud.meeting.get(db=db, id=meeting_id)
        requester = crud.user.get(db=db, id=user_id)

        meeting_name = meeting.name
        target_fcm_token = crud.user.get_user_fcm_token(
            db=db, user_id=meeting.creator_id
        )
        requester_nick_name = requester.nick_name

        title = "모임 취소"
        body = f"{requester_nick_name}님이 {meeting_name} 모임에서 나갔어요."

        icon_url = settings.S3_URL + "/default_icon/Thumbnail_Icon_Notify.svg"
        data = {"meeting_id": str(meeting_id), "icon_url": str(icon_url)}
        return send_fcm_notification(title, body, [target_fcm_token], data)

    def meeting_request_approve(self, db: Session, user_id: int, meeting_id: int):
        meeting = crud.meeting.get(db=db, id=meeting_id)

        meeting_name = meeting.name
        target_fcm_token = crud.user.get_user_fcm_token(db=db, user_id=user_id)

        title = "모임 승인"
        body = f"{meeting_name} 모임에 승인되었어요."

        icon_url = settings.S3_URL + "/default_icon/Thumbnail_Icon_Notify.svg"
        data = {"meeting_id": str(meeting_id), "icon_url": str(icon_url)}
        return send_fcm_notification(title, body, [target_fcm_token], data)

    def meeting_request_reject(self, db: Session, user_id: int, meeting_id: int):
        meeting = crud.meeting.get(db=db, id=meeting_id)

        meeting_name = meeting.name
        target_fcm_token = crud.user.get_user_fcm_token(db=db, user_id=user_id)

        title = "모임 거절"
        body = f"{meeting_name} 모임에 거절되었어요."

        icon_url = settings.S3_URL + "/default_icon/Thumbnail_Icon_Notify.svg"
        data = {"meeting_id": str(meeting_id), "icon_url": str(icon_url)}
        return send_fcm_notification(title, body, [target_fcm_token], data)

    def notice_alarm(self, db: Session, title: str, content: str, notice_id: int):
        fcm_tokens = crud.user.get_all_fcm_tokens(db=db)
        icon_url = settings.S3_URL + "/default_icon/Thumbnail_notice_Icon.svg"
        data = {"notice_id": str(notice_id), "icon_url": str(icon_url)}
        return send_fcm_notification(
            title=title, body=content, fcm_tokens=fcm_tokens, data=data
        )

    def report_alarm(self, db: Session, target_id: int):
        target_fcm_token = crud.user.get_user_fcm_token(db=db, user_id=target_id)
        get_all_report = crud.report.get_by_user_id(db=db, user_id=target_id)

        title = "경고"
        body = f"서비스 이용규정 위반으로 경고가 {len(get_all_report)}회 누적되었습니다."

        icon_url = settings.S3_URL + "/default_icon/Thumbnail_reprot_icon.svg"
        data = {"icon_url": str(icon_url)}
        return send_fcm_notification(
            title=title, body=body, fcm_tokens=[target_fcm_token]
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
        meeting_name = meeting.name
        data = {"chat_id": str(chat_id)}

        # 현재 채팅창에 활성화 되어 있는 유저 제외
        chat_users_dict = crud.user.read_all_chat_users(db=db, chat_id=chat_id)
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


alarm = Alarm()
