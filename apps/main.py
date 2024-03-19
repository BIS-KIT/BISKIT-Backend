import base64, json
from dotenv import load_dotenv

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from firebase_admin import credentials, initialize_app
from fastapi.openapi.docs import get_swagger_ui_html
from sqladmin import Admin
from database.session import engine
from apscheduler.schedulers.background import BackgroundScheduler

from core.config import settings
from core.security import get_admin
from core.redis_driver import RedisDriver
from admin.base import register_all, templates_dir, AdminAuth
from api.v1.router import api_router as v1_router
from scheduler_module import meeting_active_check, user_remove_after_seven


with open("encoded_key.txt", "r") as file:
    encoded_data = file.read()

decoded_data = base64.b64decode(encoded_data).decode("utf-8")
firebase_config = json.loads(decoded_data)
# Firebase 초기화
cred = credentials.Certificate(firebase_config)

try:
    firebase_app = initialize_app(cred, {"databaseURL": settings.FIRESTORE_URL})
    print("Firebase app initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase app: {e}")

load_dotenv()

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=None,
)
app.mount("/media", StaticFiles(directory="media"), name="media")

redis_instance = RedisDriver(redis_url=f"redis://{settings.REDIS_HOST}")

scheduler = BackgroundScheduler()

authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)

admin = Admin(
    app,
    engine,
    templates_dir=templates_dir,
    authentication_backend=authentication_backend,
)
register_all(admin)

app.include_router(v1_router, prefix="/v1")


@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_admin)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.on_event("startup")
def start_scheduler():
    # 스케줄러 시작 및 작업 추가
    scheduler.add_job(meeting_active_check, "interval", minutes=1)
    scheduler.add_job(user_remove_after_seven, "interval", minutes=1)
    scheduler.start()

    # redis connect
    redis_instance.connect()


@app.on_event("shutdown")
def shutdown_scheduler():
    # 스케줄러 종료
    scheduler.shutdown()

    # redis disconnect
    redis_instance.disconnect()


# Set all CORS enabled origins
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
