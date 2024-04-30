import pytest
import firebase_admin

from crud.alarm import alarm
from tests.confest import *


def test_read_alarm(session, test_alarm):
    alarm_service = alarm.read_alarm(db=session, alarm_id=test_alarm.id)

    assert alarm_service.is_read == "true"


def test_reject_student_verification(session, test_user, test_user_ios):
    # Android
    alarm_service = alarm.reject_student_verification(db=session, user_id=test_user.id)

    assert alarm_service == None

    # Ios
    alarm_service_ios = alarm.reject_student_verification(
        db=session, user_id=test_user_ios.id
    )

    assert alarm_service == None


def test_approve_student_verification(session, test_user, test_user_ios):
    # Android
    alarm_service = alarm.approve_student_verification(db=session, user_id=test_user.id)

    assert alarm_service == None

    # Ios
    alarm_service_ios = alarm.approve_student_verification(
        db=session, user_id=test_user_ios.id
    )

    assert alarm_service == None


def test_meeting_request_alarm(session, test_meeting, test_user, test_user_ios):
    # Android
    alarm_service = alarm.create_meeting_request(
        db=session, user_id=test_user.id, meeting_id=test_meeting.id
    )

    assert alarm_service == None

    # Ios
    alarm_service_ios = alarm.create_meeting_request(
        db=session, user_id=test_user_ios.id, meeting_id=test_meeting.id
    )

    assert alarm_service == None


def test_exit_meeting_alarm(session, test_user, test_meeting, test_user_ios):

    alarm_service = alarm.exit_meeting(
        db=session, user_id=test_user.id, meeting_id=test_meeting.id, is_fire=False
    )

    assert alarm_service == None

    # Ios
    alarm_service_ios = alarm.exit_meeting(
        db=session, user_id=test_user_ios.id, meeting_id=test_meeting.id, is_fire=False
    )

    assert alarm_service == None


def test_request_approve_alarm(session, test_user, test_meeting, test_user_ios):
    alarm_service = alarm.meeting_request_approve(
        db=session, user_id=test_user.id, meeting_id=test_meeting.id
    )

    assert alarm_service == None

    # Ios
    alarm_service_ios = alarm.meeting_request_approve(
        db=session, user_id=test_user_ios.id, meeting_id=test_meeting.id
    )

    assert alarm_service == None


def test_request_reject_alarm(session, test_user, test_meeting, test_user_ios):
    alarm_service = alarm.meeting_request_reject(
        db=session, user_id=test_user.id, meeting_id=test_meeting.id
    )

    assert alarm_service == None

    # Ios
    alarm_service_ios = alarm.meeting_request_reject(
        db=session, user_id=test_user_ios.id, meeting_id=test_meeting.id
    )

    assert alarm_service == None


def test_notice_alarm(session, test_notice, test_user_ios, test_user):
    alarm_service = alarm.notice_alarm(
        db=session,
        title=test_notice.title,
        content=test_notice.content,
        notice_id=test_notice.id,
    )

    assert alarm_service == True


def test_report_alarm(session, test_user, test_user_ios):
    alarm_service = alarm.report_alarm(db=session, target_id=test_user.id)

    assert alarm_service == None

    # Ios
    alarm_service_ios = alarm.report_alarm(db=session, target_id=test_user_ios.id)

    assert alarm_service == None


@pytest.mark.skip()
def test_chat_alarm(session, test_user, test_meeting, test_user_ios):
    alarm_service = alarm.chat_alarm()

    assert alarm_service == None
