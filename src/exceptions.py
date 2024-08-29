from fastapi import HTTPException


class ErrorHTTPException(HTTPException):
    def __init__(self, status_code: int, error_code: int, detail: str):
        super().__init__(status_code, detail)
        self.error_code = error_code
