from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean

from models.base import ModelBase


class System(ModelBase):
    system_language = Column(String)
    main_alarm = Column(Boolean, default=True)
    etc_alarm = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref="systems")


class Report(ModelBase):
    report_type = Column(String)
    reason = Column(String, nullable=True)
    status = Column(String)

    target_id = Column(Integer, ForeignKey("user.id"))
    reporter_id = Column(Integer, ForeignKey("user.id"))

    target = relationship(
        "User", foreign_keys=[target_id], backref="reports_received", uselist=False
    )
    reporter = relationship(
        "User", foreign_keys=[reporter_id], backref="reports_made", uselist=False
    )


class Notice(ModelBase):
    title = Column(String)
    content = Column(String)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref="notice")
