from sqladmin import ModelView, Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from jose import jwt
from datetime import timedelta

from core.config import settings
from core.security import create_access_token
from models.user import User, AccountDeletionRequest
from models.profile import StudentVerification
from models.system import Report, Contact
from models.utility import Tag, Topic

import os, secrets
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
    column_sortable_list = [User.created_time]
    column_list = [
        User.created_time,
        User.id,
        User.name,
        User.birth,
        "nick_name",
        User.email,
        User.gender,
        User.sns_type,
    ]


class DeletionRequestAdmin(BaseAdmin, model=AccountDeletionRequest):
    column_list = [
        AccountDeletionRequest.id,
        AccountDeletionRequest.created_time,
        AccountDeletionRequest.reason,
    ]


class ContactAdmin(BaseAdmin, model=Contact):
    column_searchable_list = [Contact.user_id]
    column_sortable_list = [Contact.created_time]
    column_list = [Contact.created_time, Contact.id, Contact.user_id, Contact.content]


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
        Report.created_time,
        Report.content_type,
        Report.content_id,
        Report.reason,
        Report.status,
        "reporter_name",
        "nick_name",
    ]
    list_template = "report_list.html"
    form_columns = [Report.reason]
    column_sortable_list = [Report.created_time]


class StudentVerificationAdmin(BaseAdmin, model=StudentVerification):
    can_edit = False
    list_template = "photo_list.html"
    column_labels = dict(name="Name")
    column_sortable_list = [
        StudentVerification.created_time,
        StudentVerification.verification_status,
    ]
    column_list = [
        StudentVerification.created_time,
        StudentVerification.id,
        StudentVerification.student_card,
        StudentVerification.verification_status,
        "user_name",
        "user_birth",
        "university",
        "department",
        "education_status",
    ]


def register_all(admin: Admin):
    admin.add_view(UserAdmin)
    admin.add_view(StudentVerificationAdmin)
    admin.add_view(ReportAdmin)
    admin.add_view(ContactAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(TopicAdmin)
    admin.add_view(DeletionRequestAdmin)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        correct_username = secrets.compare_digest(username, settings.DOCS_USER)
        correct_password = secrets.compare_digest(password, settings.DOCS_PW)
        if not (correct_username and correct_password):
            return False

        hundred_years = timedelta(days=365 * 100)
        token = create_access_token(data={"sub": username}, expires_delta=hundred_years)

        request.session.update({"token": token})

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        username = payload.get("sub")
        correct_username = secrets.compare_digest(username, settings.DOCS_USER)
        if not correct_username:
            return False

        return True
