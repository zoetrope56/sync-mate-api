from datetime import datetime
from pydantic import BaseModel, field_serializer


class CharacterCreate(BaseModel):
    name: str


class CharacterResponse(BaseModel):
    id: int
    name: str
    level: int
    exp: int
    happiness: int
    hunger: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class CharacterInteractResponse(BaseModel):
    character: CharacterResponse
    leveled_up: bool
    message: str
