import factory

from .base import BaseFactory

from models import user as user_models
from crud.user import get_password_hash


class UserFactory(BaseFactory):

    email = factory.Faker("email")
    password = factory.LazyFunction(lambda: get_password_hash("testpassword"))
    name = factory.Faker("name")
    birth = factory.Faker("date")
    gender = factory.Iterator(["male", "female"])
    fcm_token = "dX2jZUJjTQKE_N3trPHQNW:APA91bGHlmm5sMqN4f3vXXF-hY_g593GKo9JdiRABeH2rGj9CW-_WbVb8xybLfI3rckHR47rasfd9qMI-dDSmMtk5ofj5ckafCpvOeTojsDKlthnFgKlTq6tLFqFhAicSz6rhPEqJV8p"
    is_active = True
    is_admin = False

    class Meta:
        model = user_models.User

    class Params:
        with_nationality = factory.Trait(
            user_nationality=factory.RelatedFactory(
                "tests.factories.user_factory.UserNationalityFactory",
                "user",
            )
        )

        with_profile = factory.Trait(
            profile=factory.RelatedFactory(
                "tests.factories.profile_factory.ProfileFactory",
                "user",
                with_university=True,
                with_language=True,
                with_student_card=True,
                with_introduction=True,
            )
        )


class UserNationalityFactory(BaseFactory):

    user = factory.SubFactory(UserFactory)
    nationality = factory.SubFactory(
        "tests.factories.utility_factory.NationalityFactory"
    )

    class Meta:
        model = user_models.UserNationality


class ConsentFactory(BaseFactory):

    terms_mandatory = True
    terms_optional = True
    terms_push = True
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = user_models.Consent


class DeletionRequestFactory(BaseFactory):

    reason = factory.Faker("word")

    class Meta:
        model = user_models.AccountDeletionRequest
