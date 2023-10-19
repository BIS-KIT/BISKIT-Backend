from fastapi import APIRouter

from api.v1.endpoints import user, profile, utility, login, chat, admin

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(user.router, tags=["user"])
api_router.include_router(profile.router, tags=["profile"])
api_router.include_router(utility.router, tags=["utility"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(admin.router, tags=["admin"])
