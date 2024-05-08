import base64, json, time
from dotenv import load_dotenv

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from firebase_admin import credentials, initialize_app
from fastapi.openapi.docs import get_swagger_ui_html
from sqladmin import Admin
from database.session import engine
from apscheduler.schedulers.background import BackgroundScheduler

from core.config import settings
from core.security import get_admin
from core.redis_driver import redis_driver
from admin.base import register_all, templates_dir, AdminAuth
from api.v1.router import api_router as v1_router
from scheduler_module import (
    meeting_active_check,
    user_remove_after_seven,
    meeting_time_alarm,
)


encoded_data = settings.ENCODED_KEY

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


class RequestTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        print(
            f"Request: {request.method} {request.url.path} - Completed in {process_time:.4f} secs"
        )
        return response


# 미들웨어 추가
app.add_middleware(RequestTimeMiddleware)


@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_admin)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.on_event("startup")
async def start_event():
    scheduler.add_job(meeting_active_check, "interval", minutes=5)
    # 일단 삭제 하지 않고 비활성화 상태로둠
    # scheduler.add_job(user_remove_after_seven, "interval", hours=6)
    scheduler.add_job(meeting_time_alarm, "interval", minutes=1)

    if scheduler.state == 0:
        scheduler.start()

    if not settings.DEBUG:
        from init_data import run_init_data

        run_init_data()

    # redis connect
    redis_driver.connect()


@app.on_event("shutdown")
async def shutdown_event():
    # 스케줄러 종료
    scheduler.shutdown()


# Set all CORS enabled origins
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
