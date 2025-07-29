from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router
from app.api.middleware import error_handler_middleware, request_id_middleware, timing_middleware
from app.core.logging import setup_logging
from app.core.config import get_settings
import uvicorn

# Setup logging
logger = setup_logging()
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Multi-Agent System API",
    description="A modular AI agent system with specialized agents for data processing, decision-making, and communication",
    version="1.0.0",
    debug=settings.debug
)

# Add middleware
app.middleware("http")(error_handler_middleware)
app.middleware("http")(request_id_middleware)
app.middleware("http")(timing_middleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info("All systems initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )