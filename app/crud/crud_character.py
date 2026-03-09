from sqlalchemy.orm import Session
from app.models.character import Character
from app.schemas.character import CharacterCreate


def get_character_by_user(db: Session, user_id: int) -> Character | None:
    return db.query(Character).filter(Character.user_id == user_id).first()


def create_character(db: Session, data: CharacterCreate, user_id: int) -> Character:
    character = Character(**data.model_dump(), user_id=user_id)
    db.add(character)
    db.commit()
    db.refresh(character)
    return character


def save_character(db: Session, character: Character) -> Character:
    db.commit()
    db.refresh(character)
    return character
