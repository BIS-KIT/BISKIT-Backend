from sqladmin import ModelView, Admin

from models.user import User
from models.profile import StudentVerification


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name]


class StudentVerificationAdmin(ModelView, model=StudentVerification):
    column_list = [
        StudentVerification.student_card,
        StudentVerification.verification_status,
    ]


def register_all(admin: Admin):
    admin.add_view(UserAdmin)
    admin.add_view(StudentVerificationAdmin)
