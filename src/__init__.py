from fastapi import FastAPI, Request, status
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.exceptions import BooklyException
from fastapi.responses import JSONResponse
from .middleware import register_middleware
import logging


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
    lifespan=life_span,
)


@app.exception_handler(BooklyException)
async def bookly_exception_handler(request: Request, exc: BooklyException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.__class__.__name__, "message": exc.message},
    )


@app.exception_handler(500)
async def internal_server_error(request: Request, exc: Exception):
    # logging.
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "internal_server_errror", "message": "Something went wrong."},
    )


register_middleware(app)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])
