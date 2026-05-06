from fastapi import APIRouter, Depends, Form, HTTPException, status
from app.api.v1.deps import get_user_repo
from app.core.security import create_access_token, get_password_hash, verify_password
from app.domain.user.repository import UserRepository
from app.schemas.user import Token, UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, repo: UserRepository = Depends(get_user_repo)):
    if repo.get_by_email(data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return repo.create(email=data.email, hashed_password=get_password_hash(data.password))


@router.post("/login", response_model=Token)
def login(
    email: str = Form(...),
    password: str = Form(...),
    repo: UserRepository = Depends(get_user_repo),
):
    user = repo.get_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}
