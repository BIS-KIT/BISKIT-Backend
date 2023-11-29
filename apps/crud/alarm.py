from firebase_admin import messaging

from firebase_admin import firestore
from sqlalchemy.orm import Session
from typing import List

import crud


def send_fcm_notification(title: str, body: str, fcm_tokens: List[str], data=None):
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
        return f"Successfully sent message: {response}"
    except Exception as e:
        return f"Error sending message: {e}"


class Alarm:
    def _get_user_info_and_meeting(self, db: Session, user_id: int, meeting_id: int):
        fcm_token, nick_name = crud.user.get_user_fcm_token_with_name(
            db=db, user_id=user_id
        )
        meeting = crud.meeting.get(db=db, id=meeting_id)
        if not fcm_token:
            raise ValueError("fcm_token is None")
        return fcm_token, nick_name, meeting

    def create_meeting_request(self, db: Session, user_id: int, meeting_id: int):
        fcm_token, nick_name, meeting = self._get_user_info_and_meeting(
            db, user_id, meeting_id
        )
        title = "모임 신청"
        body = f"{nick_name}님이 {meeting.name} 모임에 신청했어요."
        data = {"meeting_id": meeting_id}
        return send_fcm_notification(title, body, [fcm_token], data)

    def exit_meeting(self, db: Session, user_id: int, meeting_id: int):
        fcm_token, nick_name, meeting = self._get_user_info_and_meeting(
            db, user_id, meeting_id
        )
        title = "모임 취소"
        body = f"{nick_name}님이 {meeting.name} 모임에서 나갔어요."
        data = {"meeting_id": meeting_id}
        return send_fcm_notification(title, body, [fcm_token], data)

    def meeting_request_approve(self, db: Session, user_id: int, meeting_id: int):
        fcm_token, nick_name, meeting = self._get_user_info_and_meeting(
            db, user_id, meeting_id
        )
        title = "모임 승인"
        body = f"{meeting.name} 모임에 승인되었어요."
        data = {"meeting_id": meeting_id}
        return send_fcm_notification(title, body, [fcm_token], data)

    def meeting_request_reject(self, db: Session, user_id: int, meeting_id: int):
        fcm_token, nick_name, meeting = self._get_user_info_and_meeting(
            db, user_id, meeting_id
        )
        title = "모임 거절"
        body = f"{meeting.name} 모임에 거절되었어요."
        data = {"meeting_id": meeting_id}
        return send_fcm_notification(title, body, [fcm_token], data)

    def notice_alarm(self, db: Session, title: str, content: str, notice_id: int):
        fcm_tokens = crud.user.get_all_fcm_tokens(db=db)
        data = {"notice_id": notice_id}
        return send_fcm_notification(
            title=title, body=content, fcm_tokens=fcm_tokens, data=data
        )

    def chat_alarm(self, db: Session, chat_id: str):
        # Firebase Realtime Database에서 채팅방 데이터 읽기
        firebase_db = firestore.client()
        # 특정 문서 참조
        doc_ref = firebase_db.collection("ChatRoom").document(chat_id)
        doc = doc_ref.get()

        # 문서 존재 여부 확인 및 필요한 필드 추출
        if not doc.exists:
            raise ValueError("Chat Not Found")

        # 현재 채팅창에 활성화 되어 있는 유저 제외
        chat_users_dict = crud.user.read_all_chat_users(db=db, chat_id=chat_id)
        doc_data = doc.to_dict()
        connecting_users = doc_data.get("connectingUsers", [])
        remaining_users = {
            user_id: fcm_token
            for user_id, fcm_token in chat_users_dict.items()
            if user_id not in connecting_users
        }

        # TODO : 각 유저의 차단 유저 제외


alarm = Alarm()
