from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response, JSONResponse
from typing import Callable, Awaitable
import time, logging
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("uvicorn.access")

logger.disabled = True


def register_middleware(app: FastAPI):
    app.add_middleware(TrustedHostMiddleware, www_redirect=True, allowed_hosts=["*"])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
        # allow_origin_regex
    )

    # app.add_middleware(HTTPSRedirectMiddleware) note: only used in production

    @app.middleware("http")
    async def custom_logging(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        client = f"{request.client.host}: {request.client.port}"  # type: ignore
        message = f"HOST: {client}  PROCESS_TIME: {process_time}s"
        print(message)
        # response.headers["X-Process-Time"] = str(process_time)
        return response

    @app.middleware("http")
    async def get_request_info(request: Request, call_next):
        print(f"INCOMING: {request.method} {request.url.path}")

        response = await call_next(request)

        print(f"RESPONSE: STATUS {response.status_code}")
        return response

    # auth middleware is not necessary if dependencies are used else:

    # @app.middleware("http")
    # async def authorization_middleware(
    #     request: Request, call_next: Callable[[Request], Awaitable[Response]]
    # ):
    # public_paths = [
    #     "/health",
    #     "/docs",
    #     "/redoc",
    #     "/openapi.json",
    #     "/api/v1/auth/login",
    #     "/api/v1/auth/signup",
    #     "api/v1/auth/refresh"
    # ]
    #     if not "Authorization" in request.headers:
    #         return JSONResponse(
    #             content={
    #                 "message": "Not Authenticated",
    #                 "resolution": "Please provide the right credentials to proceed",
    #             }
    #         )
    #     response = await call_next(request)

    #     return response
