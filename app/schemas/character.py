from datetime import datetime
from pydantic import BaseModel


class CharacterCreate(BaseModel):
    name: str


class CharacterResponse(BaseModel):
    id: int
    user_id: int
    name: str
    level: int
    exp: int
    happiness: int
    hunger: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CharacterInteractResponse(BaseModel):
    character: CharacterResponse
    leveled_up: bool
    message: str
