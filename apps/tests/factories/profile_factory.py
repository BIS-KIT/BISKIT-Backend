import factory

from .base import BaseFactory
from .user_factory import UserFactory
from .utility_factory import UniversityFactory, LanguageFactory

from models import profile as profile_models


class ProfileFactory(BaseFactory):

    class Meta:
        model = profile_models.Profile

    profile_photo = factory.Faker("image_url")
    nick_name = factory.Faker("name")
    context = factory.Faker("text")
    is_default_photo = False
    user = factory.SubFactory(UserFactory)


class UserUniversityFactory(BaseFactory):

    class Meta:
        model = profile_models.UserUniversity

    department = factory.Iterator(
        ["UNDERGRADUATE", "GRADUATE", "EXCHANGE_STUDENT", "LANGUAGE_INSTITUTE"]
    )
    education_status = factory.Iterator(["undergraduate", "graduate"])
    university = factory.RelatedFactoryList(LanguageFactory, size=2)
    user = factory.SubFactory(UserFactory)
    profile = factory.SubFactory(ProfileFactory)


class AvailableLanguageFactory(BaseFactory):

    class Meta:
        model = profile_models.AvailableLanguage

    level = factory.Iterator(["beginner", "intermediate", "advanced"])
    language = factory.SubFactory(LanguageFactory)
    profile = factory.SubFactory(ProfileFactory)


class IntroductionFactory(BaseFactory):

    class Meta:
        model = profile_models.Introduction

    keyword = factory.Faker("word")
    context = factory.Faker("text")
    profile = factory.SubFactory(ProfileFactory)


class StudentVerificationFactory(BaseFactory):

    class Meta:
        model = profile_models.StudentVerification

    student_card = factory.Faker("uuid4")
    verification_status = factory.Iterator(["pending", "approved", "rejected"])
    profile = factory.SubFactory(ProfileFactory)
