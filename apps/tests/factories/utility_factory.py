import factory

from .base import BaseFactory
from models import utility as utility_models


class NationalityFactory(BaseFactory):

    kr_name = factory.Iterator(["대한민국", "미국"])
    en_name = factory.Iterator(["Korea", "USA"])
    code = factory.Iterator(["kr", "usa"])

    class Meta:
        model = utility_models.Nationality


class LanguageFactory(BaseFactory):

    kr_name = factory.Iterator(["한국어", "영어"])
    en_name = factory.Iterator(["Korean", "English"])

    class Meta:
        model = utility_models.Language


class UniversityFactory(BaseFactory):

    kr_name = factory.Iterator(["서울대학교", "고려대학교"])
    en_name = factory.Faker("name")
    campus_type = factory.Faker("word")
    location = factory.Faker("address")

    class Meta:
        model = utility_models.University


class TagFactory(BaseFactory):

    kr_name = factory.Faker("word")
    en_name = factory.Faker("word")

    class Meta:
        model = utility_models.Tag


class TopicFactory(BaseFactory):

    kr_name = factory.Faker("word")
    en_name = factory.Faker("word")

    class Meta:
        model = utility_models.Topic
