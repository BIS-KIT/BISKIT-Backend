import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyDecimal, FuzzyText

from .base import BaseFactory
from models import meeting as meeting_models
from schemas.enum import ReultStatusEnum


class MeetingFactory(BaseFactory):

    name = factory.Faker("name")
    location = factory.Faker("address")
    description = FuzzyText(length=40)
    description = factory.Faker("paragraph")
    meeting_time = factory.Faker("future_datetime", end_date="+10d")
    max_participants = FuzzyInteger(5, 10)
    current_participants = 0
    korean_count = 0
    foreign_count = 0

    chat_id = factory.Sequence(lambda n: f"chat_{n}")
    place_url = factory.Faker("url")
    x_coord = FuzzyDecimal(-180.0, 180.0)
    y_coord = FuzzyDecimal(-90.0, 90.0)

    image_url = factory.Faker("image_url")
    is_active = FuzzyChoice([True, False])
    is_public = FuzzyChoice([True, False])

    university = factory.LazyAttribute(
        lambda obj: (
            obj.creator.user_university.university
            if obj.creator.user_university
            else None
        )
    )
    creator = factory.SubFactory("tests.factories.user_factory.UserFactory")

    class Meta:
        model = meeting_models.Meeting

    class Params:
        with_review = factory.Trait(
            user_nationality=factory.RelatedFactory(
                "tests.factories.meeting_factories.ReviewFactory",
                "user",
            )
        )

    @factory.post_generation
    def meeting_users(self, create, extracted, user_count: int = 2, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                MeetingUserFactory.create(meeting=self, user=user)
        else:
            MeetingUserFactory.create_batch(user_count, meeting=self)

    @factory.post_generation
    def meeting_languages(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for language in extracted:
                MeetingLanguageFactory.create(meeting=self, language=language)
        else:
            MeetingLanguageFactory.create_batch(2, meeting=self)

    @factory.post_generation
    def meeting_topics(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for topic in extracted:
                MeetingTopicFactory.create(meeting=self, topic=topic)
        else:
            MeetingTopicFactory.create_batch(2, meeting=self)

    @factory.post_generation
    def meeting_tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in extracted:
                MeetingTagFactory.create(meeting=self, tag=tag)
        else:
            MeetingTagFactory.create_batch(2, meeting=self)


class MeetingUserFactory(BaseFactory):

    status = ReultStatusEnum.PENDING

    user = factory.SubFactory("tests.factories.user_factory.UserFactory")
    meeting = factory.SubFactory(MeetingFactory)

    class Meta:
        model = meeting_models.MeetingUser


class MeetingLanguageFactory(BaseFactory):

    language = factory.SubFactory("tests.factories.utility_factory.LanguageFactory")
    meeting = factory.SubFactory(MeetingFactory)

    class Meta:
        model = meeting_models.MeetingLanguage


class MeetingTagFactory(BaseFactory):

    tag = factory.SubFactory("tests.factories.utility_factory.TagFactory")
    meeting = factory.SubFactory(MeetingFactory)

    class Meta:
        model = meeting_models.MeetingTag


class MeetingTopicFactory(BaseFactory):

    topic = factory.SubFactory("tests.factories.utility_factory.TopicFactory")
    meeting = factory.SubFactory(MeetingFactory)

    class Meta:
        model = meeting_models.MeetingTopic


class ReviewFactory(BaseFactory):

    context = FuzzyText(length=40)
    image_url = factory.Faker("image_url")
    meeting = factory.SubFactory(MeetingFactory)
    creator = factory.SubFactory("tests.factories.user_factory.UserFactory")

    class Meta:
        model = meeting_models.Review
