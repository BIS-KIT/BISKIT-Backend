import base64, json
from dotenv import load_dotenv

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from firebase_admin import credentials, initialize_app

from core.config import settings
from api.v1.router import api_router as v1_router


with open("encoded_key.txt", "r") as file:
    encoded_data = file.read()

decoded_data = base64.b64decode(encoded_data).decode("utf-8")
firebase_config = json.loads(decoded_data)
# Firebase 초기화
cred = credentials.Certificate(firebase_config)
initialize_app(cred)

load_dotenv()

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(v1_router, prefix="/v1")
# Set all CORS enabled origins
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
