from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

import crud
from database.session import get_db
from schemas.utility import LanguageBase, UniversityBase, NationalityBase
from models.utility import Language, University, Nationality


router = APIRouter()


@router.get("/languages", response_model=List[LanguageBase])
def get_languages(db: Session = Depends(get_db)):
    languages = db.query(Language).all()
    return languages


@router.get("/universty", response_model=List[UniversityBase])
def get_universities(db: Session = Depends(get_db)):
    universities = db.query(University).all()
    return universities


@router.get("/nationality", response_model=List[NationalityBase])
def get_Countries(db: Session = Depends(get_db)):
    Countries = db.query(Nationality).all()
    return Countries
