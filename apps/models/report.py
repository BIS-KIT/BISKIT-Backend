from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from models.base import ModelBase

class Report(ModelBase):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(Enum("chat", "meeting"), index=True)
    target_id = Column(Integer, index=True)
    reason = Column(String, index=True)
