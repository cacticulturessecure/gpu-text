import logging
import json
from datetime import datetime
from fastapi import Request
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api")
logger.setLevel(logging.INFO)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = datetime.now()
        response = await call_next(request)
        duration = (datetime.now() - start_time).total_seconds()
        
        log_dict = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "client_ip": request.client.host
        }
        logger.info(json.dumps(log_dict))
        return response
