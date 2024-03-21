import pytest

from .base import session
from .user_fixture import test_user
from .utils import create_test_user
from models import system as system_models


@pytest.fixture(scope="function")
def test_system(session, test_user):
    system = system_models.System(user_id=test_user.id, system_language="kr")
    session.add(system)
    session.commit()
    return system


@pytest.fixture(scope="function")
def test_report(session, test_user):
    test_reason = "test_reason"
    report = system_models.Report(
        reason=test_reason, reporter_id=test_user.id, status="PENDING"
    )

    session.add(report)
    session.commit()
    return report


@pytest.fixture(scope="function")
def test_notice(session, test_user):
    notice = system_models.Notice(
        title="test_title", content="test_content", user_id=test_user.id
    )

    session.add(notice)
    session.commit()
    return notice


@pytest.fixture(scope="function")
def test_contact(session, test_user):
    contact = system_models.Contact(content="test_content", user_id=test_user.id)

    session.add(contact)
    session.commit()
    return contact


@pytest.fixture(scope="function")
def test_ban(session, test_user, test_language, test_nationality, test_university):
    target_user = create_test_user(
        session=session,
        test_language=test_language,
        test_nationality=test_nationality,
        test_university=test_university,
    )
    ban = system_models.Ban(target_id=target_user["id"], reporter_id=test_user.id)

    session.add(ban)
    session.commit()
    return ban
