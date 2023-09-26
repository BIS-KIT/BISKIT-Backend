from sqlalchemy.orm import Session
from models.utility import Language, Nationality, University


class CRUDUtility:
    def get(
        self,
        db: Session,
        language_id: int = None,
        nationality_id: int = None,
        university_id: int = None,
    ):
        if language_id:
            return db.query(Language).filter(Language.id == language_id)
        if nationality_id:
            return (
                db.query(Nationality).filter(Nationality.id == nationality_id)
            )
        if university_id:
            return db.query(University).filter(University.id == university_id)


utility = CRUDUtility()
