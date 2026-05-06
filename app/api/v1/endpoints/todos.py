from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.deps import get_character_repo, get_current_user, get_todo_repo
from app.domain.character.repository import CharacterRepository
from app.domain.todo.repository import TodoRepository
from app.domain.user.entity import User
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate

router = APIRouter()


@router.get("/", response_model=list[TodoResponse])
def list_todos(
    skip: int = 0,
    limit: int = 100,
    repo: TodoRepository = Depends(get_todo_repo),
    current_user: User = Depends(get_current_user),
):
    return repo.get_list(user_id=current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    data: TodoCreate,
    repo: TodoRepository = Depends(get_todo_repo),
    current_user: User = Depends(get_current_user),
):
    return repo.create(data, user_id=current_user.id)


@router.patch("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    data: TodoUpdate,
    todo_repo: TodoRepository = Depends(get_todo_repo),
    char_repo: CharacterRepository = Depends(get_character_repo),
    current_user: User = Depends(get_current_user),
):
    todo = todo_repo.get(todo_id, user_id=current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    completing = data.is_completed is True and not todo.is_completed
    updated = todo_repo.update(todo, data)
    if completing:
        character = char_repo.get_by_user(user_id=current_user.id)
        if character:
            character.apply_todo_complete()
            char_repo.save(character)
    return updated


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    repo: TodoRepository = Depends(get_todo_repo),
    current_user: User = Depends(get_current_user),
):
    todo = repo.get(todo_id, user_id=current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    repo.delete(todo)
