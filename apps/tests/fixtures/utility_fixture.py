import pytest

from ..factories import (
    UniversityFactory,
    NationalityFactory,
    LanguageFactory,
    TopicFactory,
    TagFactory,
)


@pytest.fixture(scope="function")
def test_university():
    return UniversityFactory()


@pytest.fixture(scope="function")
def test_language():
    return LanguageFactory()


@pytest.fixture(scope="function")
def test_tag():
    return TagFactory()


@pytest.fixture(scope="function")
def test_topic():
    return TopicFactory()


@pytest.fixture(scope="function")
def test_nationality():
    nationality1 = NationalityFactory(kr_name="대한민국", code="kr")
    nationality2 = NationalityFactory(kr_name="미국")
    return nationality1, nationality2
