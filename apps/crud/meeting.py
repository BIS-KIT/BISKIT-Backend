from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.meeting import Meeting, MeetingLanguage, MeetingTag, MeetingTopic, MeetingUser
from schemas.meeting import meetingCreateUpdate


class CURDMeeting(CRUDBase[Meeting, meetingCreateUpdate, meetingCreateUpdate]):
    def create(self, db: Session, *, obj_in: meetingCreateUpdate) -> Meeting:
        pass


meeting = CURDMeeting(Meeting)
