from pytest_factoryboy import register

from .profile_factory import (
    ProfileFactory,
    UserUniversityFactory,
    AvailableLanguageFactory,
    IntroductionFactory,
    StudentVerificationFactory,
)
from .user_factory import (
    UserFactory,
    UserNationalityFactory,
    ConsentFactory,
    DeletionRequestFactory,
)
from .utility_factory import (
    NationalityFactory,
    LanguageFactory,
    UniversityFactory,
    TagFactory,
    TopicFactory,
)
