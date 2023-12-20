from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean

from models.base import ModelBase


class System(ModelBase):
    system_language = Column(String)
    main_alarm = Column(Boolean, default=True)
    etc_alarm = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    user = relationship(
        "User", backref=backref("systems", cascade="all, delete-orphan")
    )


class Report(ModelBase):
    reason = Column(String, nullable=True)
    status = Column(String)

    content_type = Column(String, nullable=True)
    content_id = Column(Integer, nullable=True)

    reporter_id = Column(Integer, ForeignKey("user.id"))
    reporter = relationship(
        "User",
        foreign_keys=[reporter_id],
        backref=backref("reports_made", cascade="all, delete-orphan"),
        uselist=False,
    )

    @property
    def reporter_name(self):
        return self.reporter.name

    @property
    def nick_name(self):
        return self.reporter.nick_name


class Notice(ModelBase):
    title = Column(String)
    content = Column(String)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref="notice")


class Ban(ModelBase):
    target_id = Column(Integer, ForeignKey("user.id"))
    reporter_id = Column(Integer, ForeignKey("user.id"))

    target = relationship(
        "User",
        foreign_keys=[target_id],
        backref=backref("banned_received", cascade="all, delete-orphan"),
        uselist=False,
    )
    reporter = relationship(
        "User",
        foreign_keys=[reporter_id],
        backref=backref("ban_made", cascade="all, delete-orphan"),
        uselist=False,
    )


class Contact(ModelBase):
    content = Column(String)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(
        "User", backref=backref("contact", cascade="all, delete-orphan")
    )
