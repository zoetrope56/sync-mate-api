from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.deps import get_character_repo, get_current_user
from app.domain.character.repository import CharacterRepository
from app.domain.user.entity import User
from app.schemas.character import CharacterCreate, CharacterInteractResponse, CharacterResponse

router = APIRouter()


def _get_character_or_404(repo: CharacterRepository, user_id: int):
    character = repo.get_by_user(user_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
def create_character(
    data: CharacterCreate,
    repo: CharacterRepository = Depends(get_character_repo),
    current_user: User = Depends(get_current_user),
):
    if repo.get_by_user(current_user.id):
        raise HTTPException(status_code=400, detail="Character already exists")
    return repo.create(data, user_id=current_user.id)


@router.get("/", response_model=CharacterResponse)
def get_character(
    repo: CharacterRepository = Depends(get_character_repo),
    current_user: User = Depends(get_current_user),
):
    return _get_character_or_404(repo, current_user.id)


@router.post("/interact", response_model=CharacterInteractResponse)
def interact(
    repo: CharacterRepository = Depends(get_character_repo),
    current_user: User = Depends(get_current_user),
):
    character = _get_character_or_404(repo, current_user.id)
    leveled_up = character.apply_interact()
    repo.save(character)
    return {
        "character": character,
        "leveled_up": leveled_up,
        "message": "캐릭터를 쓰다듬었습니다!",
    }
