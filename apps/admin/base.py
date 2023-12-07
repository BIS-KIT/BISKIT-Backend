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


class BaseAdmin(ModelView):
    can_create = False
    can_edit = False


class UserAdmin(BaseAdmin, model=User):
    column_labels = dict(name="Name", id="id")
    column_searchable_list = [User.name, User.id]
    column_list = [User.id, User.name, User.birth, "nick_name"]


class ContactAdmin(BaseAdmin, model=Contact):
    column_labels = dict(id="user_id")
    column_searchable_list = [Contact.user_id]
    column_list = [Contact.id, Contact.user_id, Contact.content]


class TagAdmin(BaseAdmin, model=Tag):
    column_labels = dict(name="Name", id="id")
    column_searchable_list = [Tag.kr_name, Tag.en_name, Tag.id]
    column_sortable_list = [Tag.is_home, Tag.is_custom]
    column_list = [
        Tag.id,
        Tag.kr_name,
        Tag.en_name,
        Tag.is_custom,
        Tag.is_home,
    ]

    list_template = "tag_list.html"


class TopicAdmin(BaseAdmin, model=Topic):
    column_labels = dict(name="Name", id="id")
    column_searchable_list = [Topic.kr_name, Topic.en_name, Topic.id]
    column_list = [Topic.kr_name, Topic.en_name, Topic.is_custom]
    column_sortable_list = [Topic.is_custom]


class ReportAdmin(BaseAdmin, model=Report):
    column_list = [
        Report.id,
        Report.content_type,
        Report.content_id,
        Report.reason,
        Report.status,
        "user_name",
    ]
    list_template = "report_list.html"


class StudentVerificationAdmin(BaseAdmin, model=StudentVerification):
    can_edit = False
    list_template = "photo_list.html"
    column_labels = dict(name="Name")
    column_sortable_list = [StudentVerification.verification_status]
    column_list = [
        StudentVerification.id,
        StudentVerification.student_card,
        StudentVerification.verification_status,
        "user_name",
        "user_email",
        "user_birth",
    ]


def register_all(admin: Admin):
    admin.add_view(UserAdmin)
    admin.add_view(StudentVerificationAdmin)
    admin.add_view(ReportAdmin)
    admin.add_view(ContactAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(TopicAdmin)
