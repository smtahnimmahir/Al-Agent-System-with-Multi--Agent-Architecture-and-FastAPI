from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.logging import setup_logging
from app.core.exceptions import AgentException
import time
import uuid
from typing import Callable

logger = setup_logging()

async def error_handler_middleware(request: Request, call_next: Callable):
    """Global error handler middleware"""
    try:
        response = await call_next(request)
        return response
    except AgentException as e:
        logger.error(f"Agent error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "error": str(e),
                "error_type": e.__class__.__name__,
                "request_id": request.state.request_id
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_type": "UnexpectedError",
                "request_id": request.state.request_id
            }
        )

async def request_id_middleware(request: Request, call_next: Callable):
    """Add unique request ID to each request"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response

async def timing_middleware(request: Request, call_next: Callable):
    """Log request timing"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    logger.info(f"Request {request.url.path} took {process_time:.2f}s")
    
    return response