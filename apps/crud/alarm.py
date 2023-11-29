from firebase_admin import messaging
from sqlalchemy.orm import Session
from typing import List

import crud


def send_fcm_notification(title:str, body:str, fcm_tokens:List[str], data=None):
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
            ) for token in fcm_tokens
        ]
        response = messaging.send_all(messages)
        return f"Successfully sent message: {response}"
    except Exception as e:
        return f"Error sending message: {e}"


class Alarm:
    def _get_user_info_and_meeting(self, db: Session, user_id: int, meeting_id: int):
        fcm_token, nick_name = crud.user.get_user_fcm_token_with_name(db=db, user_id=user_id)
        meeting = crud.meeting.get(db=db, id=meeting_id)
        if not fcm_token:
            raise ValueError("fcm_token is None")
        return fcm_token, nick_name, meeting
    
    def create_meeting_request(self, db: Session, user_id: int, meeting_id: int):
        fcm_token, nick_name, meeting = self._get_user_info_and_meeting(db, user_id, meeting_id)
        title = "모임 신청"
        body = f"{nick_name}님이 {meeting.name} 모임에 신청했어요."
        data = {"meeting_id": meeting_id}
        return send_fcm_notification(title, body, [fcm_token], data)

    def exit_meeting(self, db: Session, user_id: int, meeting_id: int):
        fcm_token, nick_name, meeting = self._get_user_info_and_meeting(db, user_id, meeting_id)
        title = "모임 취소"
        body = f"{nick_name}님이 {meeting.name} 모임에서 나갔어요."
        data = {"meeting_id": meeting_id}
        return send_fcm_notification(title, body, [fcm_token], data)

    def meeting_request_approve(self, db: Session, user_id: int, meeting_id: int):
        fcm_token, nick_name, meeting = self._get_user_info_and_meeting(db, user_id, meeting_id)
        title = "모임 승인"
        body = f"{meeting.name} 모임에 승인되었어요."
        data = {"meeting_id": meeting_id}
        return send_fcm_notification(title, body, [fcm_token], data)

    def meeting_request_reject(self, db: Session, user_id: int, meeting_id: int):
        fcm_token, nick_name, meeting = self._get_user_info_and_meeting(db, user_id, meeting_id)
        title = "모임 거절"
        body = f"{meeting.name} 모임에 거절되었어요."
        data = {"meeting_id": meeting_id}
        return send_fcm_notification(title, body, [fcm_token], data)


    def notice_alarm(db:Session, title:str, content:str, notice_id:int):
        fcm_tokens = crud.user.get_all_fcm_tokens(db=db)  
        data = {"notice_id": notice_id}
        return send_fcm_notification(title=title, body=content, fcm_tokens=fcm_tokens, data=data)