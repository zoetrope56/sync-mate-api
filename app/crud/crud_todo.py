from sqlalchemy.orm import Session
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


def get_todos(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[Todo]:
    return db.query(Todo).filter(Todo.user_id == user_id).offset(skip).limit(limit).all()


def get_todo(db: Session, todo_id: int, user_id: int) -> Todo | None:
    return db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user_id).first()


def create_todo(db: Session, data: TodoCreate, user_id: int) -> Todo:
    todo = Todo(**data.model_dump(), user_id=user_id)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def update_todo(db: Session, todo: Todo, data: TodoUpdate) -> Todo:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, todo: Todo) -> None:
    db.delete(todo)
    db.commit()
