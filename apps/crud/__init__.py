from fastapi import HTTPException
from sqlalchemy.orm import Session

from .user import (
    user,
    verify_password,
    get_password_hash,
    send_email,
    deletion_requests,
)
from .profile import profile, save_upload_file, generate_random_string
from .utility import utility
from .chat import chat
from .meeting import meeting, review
from .system import system, report


def get_object_or_404(db: Session, model, obj_id: int):
    obj = db.query(model).filter(model.id == obj_id).first()
    if not obj:
        raise HTTPException(
            status_code=404, detail=f"{model.__name__} with id {obj_id} is not found"
        )
    return obj
