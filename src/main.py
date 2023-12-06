from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from fastapi.responses import FileResponse

from .auth.base_config import auth_backend, fastapi_users
from .auth.schemas import UserCreate, UserRead
from .config import REDIS_HOST, REDIS_PORT, STATIC
from .operations.router import router as router_operation
from .report.router import router as router_report
from .pages.router import router as router_pages
from .chat.router import router as router_chat
from .employee.router import router as router_employee
from .task.router import router as router_task


app = FastAPI(title="Task_tracker App")

favicon_path = STATIC + 'favicon.ico'

app.mount("/static", StaticFiles(directory=STATIC), name="static")

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(router_operation)
app.include_router(router_report)
app.include_router(router_pages)
app.include_router(router_chat)
app.include_router(router_employee)
app.include_router(router_task)

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "fastapi_app",
    "https://v-petrenko.ru",
    "https://vap-tech.ru",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)


@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)
