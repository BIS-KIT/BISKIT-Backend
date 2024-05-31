import factory

from .base import BaseFactory
from models import utility as utility_models


class NationalityFactory(BaseFactory):

    class Meta:
        model = utility_models.Nationality


class LanguageFactory(BaseFactory):

    class Meta:
        model = utility_models.Language


class UniversityFactory(BaseFactory):

    class Meta:
        model = utility_models.University


class TagFactory(BaseFactory):

    class Meta:
        model = utility_models.Tag


class TopicFactory(BaseFactory):

    class Meta:
        model = utility_models.Topic
