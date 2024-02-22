import pytest

from .base import session
from models import utility as utility_models


@pytest.fixture(scope="function")
def test_university(session):
    university = utility_models.University(kr_name="서울대학교 ")
    session.add(university)
    session.commit()

    return university


@pytest.fixture(scope="function")
def test_language(session):
    language = utility_models.Language(kr_name="한국어")
    session.add(language)
    session.commit()

    return language


@pytest.fixture(scope="function")
def test_tag(session):
    tag = utility_models.Tag(kr_name="네트워킹", en_name="Networking")
    session.add(tag)
    session.commit()
    return tag


@pytest.fixture(scope="function")
def test_topic(session):
    topic = utility_models.Topic(kr_name="기술", en_name="Technology")
    session.add(topic)
    session.commit()
    return topic


@pytest.fixture(scope="function")
def test_nationality(session):
    nationality1 = utility_models.Nationality(kr_name="대한민국")
    nationality2 = utility_models.Nationality(kr_name="미국")
    session.add(nationality1)
    session.add(nationality2)
    session.commit()
    return nationality1, nationality2
