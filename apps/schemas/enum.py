from enum import Enum


class genderEum(str, Enum):
    MALE = "male"
    FEMALE = "female"


class LanguageLevelEnum(str, Enum):
    BEGINNER = 5
    BASIC = 4
    INTERMEDIATE = 3
    ADVANCED = 2
    PROFICIENT = 1


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


class LogTypeEnum(str, Enum):
    ALARM = "ALARM"
    SCHEDULER = "SCHEDULER"
    DEFAULT = "DEFAULT"


def level_to_enum(level_str):
    return LanguageLevelEnum[level_str].value
