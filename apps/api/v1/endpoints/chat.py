from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Body, Depends, UploadFile,HTTPException
from sqlalchemy.orm import Session

import crud
from database.session import get_db
from schemas.chat import CahtImageCreate, ChatImageResponse
from log import log_error

router = APIRouter()

@router.post("/chat/upload",response_model=ChatImageResponse)
def upload_file_chat(
    photo: UploadFile, chat_id:str, message_id:str,db: Session = Depends(get_db)
):
    return_obj = None
    file_path = f"chat_file/{chat_id}/{photo.filename}"
    try:
        image_url = crud.save_upload_file(upload_file=photo, destination=file_path)
        chat_image = CahtImageCreate(image_url=image_url, chat_id=chat_id, message_id=message_id)
        return_obj = crud.chat.create(db=db, obj_in=chat_image)
    except Exception as e:  # 어떤 예외든지 캐치합니다.
        log_error(e)
        # 클라이언트에게 에러 메시지와 상태 코드를 반환합니다.
        raise HTTPException(status_code=500)
    return return_obj