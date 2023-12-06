from sqladmin import ModelView, Admin

from models.user import User
from models.profile import StudentVerification
from models.system import Report, Contact
from models.utility import Tag, Topic

import os
from pathlib import Path


current_file_path = os.path.abspath(__file__)
folder_path = os.path.dirname(os.path.dirname(current_file_path))

templates_dir = f"{folder_path}/admin/templates"


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name]


class ContactAdmin(ModelView, model=Contact):
    column_list = [Contact.id, Contact.user_id, Contact.content]


class TagAdmin(ModelView, model=Tag):
    column_list = [
        Tag.kr_name,
        Tag.en_name,
        Tag.is_custom,
        Tag.is_custom,
        Tag.is_custom,
    ]


class TopicAdmin(ModelView, model=Topic):
    column_list = [Topic.kr_name, Topic.en_name, Topic.is_custom, Topic.is_custom]


class ReportAdmin(ModelView, model=Report):
    column_list = [
        Report.id,
        Report.content_type,
        Report.content_id,
        Report.reason,
        Report.status,
    ]
    list_template = "report_list.html"


class StudentVerificationAdmin(ModelView, model=StudentVerification):
    can_edit = False
    list_template = "photo_list.html"
    column_list = [
        StudentVerification.id,
        StudentVerification.student_card,
        StudentVerification.verification_status,
    ]


def register_all(admin: Admin):
    admin.add_view(UserAdmin)
    admin.add_view(StudentVerificationAdmin)
    admin.add_view(ReportAdmin)
    admin.add_view(ContactAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(TopicAdmin)
