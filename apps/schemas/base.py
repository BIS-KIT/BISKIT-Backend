from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Union, Literal, Any, Type, ClassVar
from models.base import ModelBase


class CoreSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: Optional[int] = None
