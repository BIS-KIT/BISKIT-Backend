from fastapi import APIRouter

from api.v1.endpoints import user
from api.v1.endpoints import profile

api_router = APIRouter()

api_router.include_router(user.router, tags=["user"])
api_router.include_router(profile.router, tags=["user"])
