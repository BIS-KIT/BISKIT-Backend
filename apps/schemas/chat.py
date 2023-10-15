from pydantic import BaseModel
from typing import Optional

from schemas.base import CoreSchema

class ChatImageResponse(CoreSchema):
    image_url:Optional[str]=None
    chat_id:Optional[str]=None
    message_id:Optional[str]=None

class CahtImageCreate(BaseModel):
    image_url:Optional[str]=None
    chat_id:Optional[str]=None
    message_id:Optional[str]=None