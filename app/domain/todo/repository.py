from sqlalchemy.orm import Session
from app.domain.todo.entity import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


class TodoRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_list(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Todo]:
        return self._db.query(Todo).filter(Todo.user_id == user_id).offset(skip).limit(limit).all()

    def get(self, todo_id: int, user_id: int) -> Todo | None:
        return self._db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user_id).first()

    def create(self, data: TodoCreate, user_id: int) -> Todo:
        todo = Todo(**data.model_dump(), user_id=user_id)
        self._db.add(todo)
        self._db.commit()
        self._db.refresh(todo)
        return todo

    def update(self, todo: Todo, data: TodoUpdate) -> Todo:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(todo, field, value)
        self._db.commit()
        self._db.refresh(todo)
        return todo

    def delete(self, todo: Todo) -> None:
        self._db.delete(todo)
        self._db.commit()