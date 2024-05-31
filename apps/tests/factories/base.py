import factory
from factory.alchemy import SQLAlchemyModelFactory

from ..fixtures.base import TestingSessionLocal


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with TestingSessionLocal.begin() as session:
            obj = model_class(*args, **kwargs)
            session.add(obj)
            session.commit()
            return obj
