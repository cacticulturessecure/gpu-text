from fastapi import HTTPException
from typing import Dict, Any

class APIError(HTTPException):
    def __init__(self, status_code: int, detail: str, headers: Dict[str, Any] = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class ModelNotFoundError(APIError):
    def __init__(self):
        super().__init__(status_code=404, detail="Model not found")

class InvalidRequestError(APIError):
    def __init__(self, detail: str = "Invalid request"):
        super().__init__(status_code=400, detail=detail)

class ServiceUnavailableError(APIError):
    def __init__(self):
        super().__init__(status_code=503, detail="Service temporarily unavailable")
