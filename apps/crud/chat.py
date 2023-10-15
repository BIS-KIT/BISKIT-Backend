from sqlalchemy.orm import Session

from crud.base import CRUDBase
from schemas.chat import CahtImageCreate, ChatImageResponse
from models.chat import ChatImage


class CRUDChat(CRUDBase[ChatImage, CahtImageCreate, CahtImageCreate]):
    pass

chat = CRUDChat(ChatImage)