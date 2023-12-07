from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean

from models.base import ModelBase


class System(ModelBase):
    system_language = Column(String)
    main_alarm = Column(Boolean, default=True)
    etc_alarm = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    user = relationship("User", backref="systems")


class Report(ModelBase):
    reason = Column(String, nullable=True)
    status = Column(String)

    content_type = Column(String, nullable=True)
    content_id = Column(Integer, nullable=True)

    reporter_id = Column(Integer, ForeignKey("user.id"))
    reporter = relationship(
        "User", foreign_keys=[reporter_id], backref="reports_made", uselist=False
    )

    @property
    def user_name(self):
        return self.reporter.name


class Notice(ModelBase):
    title = Column(String)
    content = Column(String)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref="notice")


class Ban(ModelBase):
    target_id = Column(Integer, ForeignKey("user.id"))
    reporter_id = Column(Integer, ForeignKey("user.id"))

    target = relationship(
        "User", foreign_keys=[target_id], backref="banned_received", uselist=False
    )
    reporter = relationship(
        "User", foreign_keys=[reporter_id], backref="ban_made", uselist=False
    )


class Contact(ModelBase):
    content = Column(String)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref="contact")
