import factory
from factory.alchemy import SQLAlchemyModelFactory

from ..fixtures.base import TestingSessionLocal


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = TestingSessionLocal()
        sqlalchemy_session_persistence = "commit"
