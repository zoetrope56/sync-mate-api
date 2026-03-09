from fastapi import APIRouter
from app.api.v1.endpoints import character, todos, users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(todos.router, prefix="/todos", tags=["todos"])
api_router.include_router(character.router, prefix="/character", tags=["character"])
