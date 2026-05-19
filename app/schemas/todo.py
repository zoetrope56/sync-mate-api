from datetime import datetime
from pydantic import BaseModel, field_serializer


class TodoCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_completed: bool | None = None
    due_date: datetime | None = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    is_completed: bool
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("due_date", "created_at", "updated_at")
    def serialize_dt(self, dt: datetime | None) -> str | None:
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d %H:%M:%S")
