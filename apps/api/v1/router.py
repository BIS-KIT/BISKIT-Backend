from fastapi import APIRouter

from api.v1.endpoints import user, profile, utility, login

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(user.router, tags=["user"])
api_router.include_router(profile.router, tags=["profile"])
api_router.include_router(utility.router, tags=["utility"])
