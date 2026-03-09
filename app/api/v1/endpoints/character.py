from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.deps import get_current_user
from app.crud import crud_character
from app.db.session import get_db
from app.models.user import User
from app.schemas.character import CharacterCreate, CharacterInteractResponse, CharacterResponse
from app.services import character_logic

router = APIRouter()


def _get_character_or_404(db: Session, user_id: int):
    character = crud_character.get_character_by_user(db, user_id=user_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
def create_character(
    data: CharacterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if crud_character.get_character_by_user(db, user_id=current_user.id):
        raise HTTPException(status_code=400, detail="Character already exists")
    return crud_character.create_character(db, data=data, user_id=current_user.id)


@router.get("/", response_model=CharacterResponse)
def get_character(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_character_or_404(db, current_user.id)


@router.post("/interact", response_model=CharacterInteractResponse)
def interact(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    character = _get_character_or_404(db, current_user.id)
    leveled_up = character_logic.apply_interact(character)
    crud_character.save_character(db, character)
    return {
        "character": character,
        "leveled_up": leveled_up,
        "message": "캐릭터를 쓰다듬었습니다!",
    }
