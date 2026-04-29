from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.deps import get_current_user
from app.crud import crud_character, crud_todo
from app.db.session import get_db
from app.models.user import User
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate
from app.services import character_logic

router = APIRouter()


@router.get("/", response_model=list[TodoResponse])
def list_todos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud_todo.get_todos(db, user_id=current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud_todo.create_todo(db, data=data, user_id=current_user.id)


@router.patch("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    data: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    todo = crud_todo.get_todo(db, todo_id=todo_id, user_id=current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    completing = data.is_completed is True and not todo.is_completed
    updated = crud_todo.update_todo(db, todo=todo, data=data)
    if completing:
        character = crud_character.get_character_by_user(db, user_id=current_user.id)
        if character:
            character_logic.apply_todo_complete(character)
            crud_character.save_character(db, character)
    return updated


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    todo = crud_todo.get_todo(db, todo_id=todo_id, user_id=current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    crud_todo.delete_todo(db, todo=todo)
