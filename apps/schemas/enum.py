from enum import Enum


class genderEum(str, Enum):
    MALE = "male"
    FEMALE = "female"


class LanguageLevel(Enum):
    BEGINNER = "초보"
    BASIC = "기초"
    INTERMEDIATE = "중급"
    ADVANCED = "고급"
    PROFICIENT = "능숙"


class ReultStatusEnum(str, Enum):
    PENDING = "PENDING"
    APPROVE = "APPROVE"
    REJECTED = "REJECTED"
    UNVERIFIED = "UNVERIFIED"


class MeetingOrderingEnum(str, Enum):
    CREATED_TIME = "created_time"
    MEETING_TIME = "meeting_time"
    DEADLINE_SOON = "deadline_soon"


class TimeFilterEnum(str, Enum):
    TODAY = "TODAY"
    TOMORROW = "TOMORROW"
    THIS_WEEK = "THIS_WEEK"
    NEXT_WEEK = "NEXT_WEEK"
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class CreatorNationalityEnum(str, Enum):
    KOREAN = "KOREAN"
    FOREIGNER = "FOREIGNER"
    ALL = "ALL"


class MyMeetingEnum(str, Enum):
    APPROVE = "APPROVE"
    PENDING = "PENDING"
    PAST = "PAST"


class ImageSourceEnum(str, Enum):
    PROFILE = "PROFILE"
    STUDENT_CARD = "STUDENT_CARD"
    REVIEW = "REVIEW"
    CHATTING = "CHATTING"
