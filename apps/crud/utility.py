from sqlalchemy.orm import Session
from models.utility import Language, Nationality, University, Topic, Tag


class CRUDUtility:
    def get(
        self,
        db: Session,
        language_id: int = None,
        nationality_id: int = None,
        university_id: int = None,
    ):
        if language_id:
            return db.query(Language).filter(Language.id == language_id).first()
        if nationality_id:
            return (
                db.query(Nationality).filter(Nationality.id == nationality_id).first()
            )
        if university_id:
            return db.query(University).filter(University.id == university_id).first()

    def get_topic(db:Session, topic_id:int):
        return db.query(Topic).filter(Topic.id == topic_id).first()

    def get_tag(db:Session, tag_id:int):
        return db.query(Tag).filter(Tag.id == tag_id).first()

    def create_topic(db:Session, name:str):
        db_obj = Topic(name=name)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_tag(db:Session, name:str):
        db_obj = Tag(name=name)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_topic(db:Session, topic_id:int):
        db_obj = db.query(Topic).filter(Topic.id == topic_id).delete()
        db.commit()
        return db_obj

    def delete_tag(db:Session, tag_id:int):
        db_obj = db.query(Tag).filter(Tag.id == tag_id).delete()
        db.commit()
        return db_obj

utility = CRUDUtility()
