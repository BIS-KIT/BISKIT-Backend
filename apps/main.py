import base64, json
from dotenv import load_dotenv
from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.cors import CORSMiddleware
from firebase_admin import credentials, initialize_app
from fastapi.openapi.docs import get_swagger_ui_html

from core.config import settings
from core.security import get_admin
from api.v1.router import api_router as v1_router


with open("encoded_key.txt", "r") as file:
    encoded_data = file.read()

decoded_data = base64.b64decode(encoded_data).decode("utf-8")
firebase_config = json.loads(decoded_data)
# Firebase 초기화
cred = credentials.Certificate(firebase_config)
initialize_app(cred)

load_dotenv()

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=None,
)
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(v1_router, prefix="/v1")


@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_admin)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


# Set all CORS enabled origins
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
