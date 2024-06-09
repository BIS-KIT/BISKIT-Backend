import factory

from .base import BaseFactory
from .user_factory import UserFactory
from .utility_factory import UniversityFactory, LanguageFactory
from schemas.enum import ReultStatusEnum
from models import profile as profile_models


class ProfileFactory(BaseFactory):

    profile_photo = factory.Faker("image_url")
    nick_name = factory.Faker("name")
    context = factory.Faker("text")
    is_default_photo = False
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = profile_models.Profile

    class Params:
        with_university = factory.Trait(
            user_university=factory.RelatedFactory(
                "tests.factories.profile_factory.UserUniversityFactory", "profile"
            )
        )

        with_language = factory.Trait(
            available_language_list=factory.RelatedFactoryList(
                "tests.factories.profile_factory.AvailableLanguageFactory",
                "profile",
                size=2,
            )
        )

        with_student_card = factory.Trait(
            student_verification=factory.RelatedFactory(
                "tests.factories.profile_factory.StudentVerificationFactory", "profile"
            )
        )

        with_introduction = factory.Trait(
            introductions=factory.RelatedFactoryList(
                "tests.factories.profile_factory.IntroductionFactory", "profile", size=2
            )
        )


class UserUniversityFactory(BaseFactory):

    department = factory.Iterator(
        ["UNDERGRADUATE", "GRADUATE", "EXCHANGE_STUDENT", "LANGUAGE_INSTITUTE"]
    )
    education_status = factory.Iterator(["undergraduate", "graduate"])
    university = factory.RelatedFactory(UniversityFactory)
    user_id = factory.LazyAttribute(lambda x: x.profile.user_id)
    profile = factory.SubFactory(ProfileFactory)

    class Meta:
        model = profile_models.UserUniversity


class AvailableLanguageFactory(BaseFactory):

    level = factory.Iterator(["BEGINNER", "INTERMEDIATE", "ADVANCED"])
    language = factory.SubFactory(LanguageFactory)
    profile = factory.SubFactory(ProfileFactory)

    class Meta:
        model = profile_models.AvailableLanguage


class IntroductionFactory(BaseFactory):

    keyword = factory.Faker("word")
    context = factory.Faker("text")
    profile = factory.SubFactory(ProfileFactory)

    class Meta:
        model = profile_models.Introduction


class StudentVerificationFactory(BaseFactory):

    student_card = factory.Faker("uuid4")
    verification_status = ReultStatusEnum.APPROVE.name
    profile = factory.SubFactory(ProfileFactory)

    class Meta:
        model = profile_models.StudentVerification
