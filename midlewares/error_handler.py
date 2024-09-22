from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, FastAPI
from fastapi.responses import JSONResponse
from typing import Callable

class ErrorHander(BaseHTTPMiddleware):
  def __init__(self, app: FastAPI):
    super().__init__(app)

  async def dispatch(self, request: Request, call_next: Callable) -> Response | JSONResponse:
    try:
      response = await call_next(request)
      return response
    except Exception as e:
      return JSONResponse(status_code=500, content={"error": str(e)})