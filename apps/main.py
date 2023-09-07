from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from apps.core.config import settings
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title=settings.PROJECT_NAME)

# Set all CORS enabled origins
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
