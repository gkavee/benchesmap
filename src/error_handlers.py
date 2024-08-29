from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.exceptions import ErrorHTTPException


def error_response(status_code: int, error_code: int, message: str):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": error_code, "message": message}},
    )


def setup_error_handlers(app: FastAPI):
    @app.exception_handler(ErrorHTTPException)
    async def error_http_exception_handler(request: Request, exc: ErrorHTTPException):
        return error_response(exc.status_code, exc.error_code, exc.detail)
