from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from contextlib import asynccontextmanager
from src.db.main import init_db
# from src.db.redis import run_redis


@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"server is starting ...")
    await init_db() 
    # await run_redis()
    # print("Redis connection established")
    yield
    print(f"server has stopped")
    # print("Redis connection closed")



version = "v1"

app = FastAPI(
    version=version,
    title="Bookly",
    description="A REST API for book reviews",
    lifespan=life_span
) 



app.include_router(book_router, prefix="/api/{version}/books")
app.include_router(auth_router, prefix="/api/{version}/auth", tags=['auth'])
