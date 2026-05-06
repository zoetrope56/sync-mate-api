from sqlalchemy.orm import Session
from app.domain.character.entity import Character
from app.schemas.character import CharacterCreate


class CharacterRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_by_user(self, user_id: int) -> Character | None:
        return self._db.query(Character).filter(Character.user_id == user_id).first()

    def create(self, data: CharacterCreate, user_id: int) -> Character:
        character = Character(**data.model_dump(), user_id=user_id)
        self._db.add(character)
        self._db.commit()
        self._db.refresh(character)
        return character

    def save(self, character: Character) -> Character:
        self._db.commit()
        self._db.refresh(character)
        return character