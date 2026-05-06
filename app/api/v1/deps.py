from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.db.session import get_db
from app.domain.character.repository import CharacterRepository
from app.domain.todo.repository import TodoRepository
from app.domain.user.entity import User
from app.domain.user.repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_character_repo(db: Session = Depends(get_db)) -> CharacterRepository:
    return CharacterRepository(db)


def get_todo_repo(db: Session = Depends(get_db)) -> TodoRepository:
    return TodoRepository(db)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    repo: UserRepository = Depends(get_user_repo),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = repo.get_by_id(int(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user