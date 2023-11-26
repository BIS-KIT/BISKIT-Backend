from firebase_admin import messaging
from sqlalchemy.orm import Session

import crud


def send_fcm_notification(title, body, fcm_token, data=None):
    """
    FCM을 통해 푸시 알림을 전송하는 함수
    :param title: 알림의 제목
    :param body: 알림의 내용
    :param fcm_token: 대상 장치의 FCM 토큰
    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data,
            token=fcm_token,
        )
        response = messaging.send(message)
        return f"Successfully sent message: {response}"
    except Exception as e:
        return f"Error sending message: {e}"


class Alarm:
    def create_meeting_request(db: Session, user_id: int, meeting_id: int):
        fcm_token = crud.user.get_user_fcm_token(db=db, user_id=user_id)
        data = {"meeting_id": meeting_id}
        if not fcm_token:
            ValueError("fcm_token is None")
        res = send_fcm_notification(
            title="모임 참여 신청", body="모임에 참여 신청이 있습니다.", fcm_token=fcm_token, data=data
        )
        return res

    def cancle_meeting(db: Session, user_id: int, meeting_id: int):
        fcm_token = crud.user.get_user_fcm_token(db=db, user_id=user_id)
        data = {"meeting_id": meeting_id}
        if not fcm_token:
            ValueError("fcm_token is None")
        res = send_fcm_notification(
            title="모임 취소", body="모임이 취소되었습니다.", fcm_token=fcm_token, data=data
        )
        return res

    def meeting_request_approve(db: Session, user_id: int, meeting_id: int):
        fcm_token = crud.user.get_user_fcm_token(db=db, user_id=user_id)
        data = {"meeting_id": meeting_id}
        if not fcm_token:
            ValueError("fcm_token is None")
        res = send_fcm_notification(
            title="모임 참여 신청", body="모임 참여 신청이 승인되었습니다.", fcm_token=fcm_token, data=data
        )
        return res

    def meeting_request_reject(db: Session, user_id: int, meeting_id: int):
        fcm_token = crud.user.get_user_fcm_token(db=db, user_id=user_id)
        data = {"meeting_id": meeting_id}
        if not fcm_token:
            ValueError("fcm_token is None")
        res = send_fcm_notification(
            title="모임 참여 신청", body="모임 참여 신청이 거절되었습니다.", fcm_token=fcm_token, data=data
        )
        return res
