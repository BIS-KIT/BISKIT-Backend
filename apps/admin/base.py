from sqladmin import ModelView, Admin

from models.user import User
from models.profile import StudentVerification

import os
from pathlib import Path
from fastapi.templating import Jinja2Templates

current_file_path = os.path.abspath(__file__)
folder_path = os.path.dirname(os.path.dirname(current_file_path))

templates_dir = f"{folder_path}/admin/templates"


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name]


class StudentVerificationAdmin(ModelView, model=StudentVerification):
    list_template = "photo_list.html"
    column_list = [
        StudentVerification.id,
        StudentVerification.student_card,
        StudentVerification.verification_status,
    ]


def register_all(admin: Admin):
    admin.add_view(UserAdmin)
    admin.add_view(StudentVerificationAdmin)
