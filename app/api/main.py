from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from . import endpoints


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Create FastAPI app
app = FastAPI(
    title="Delivery Route Planning API",
    description="AI-powered delivery route planning with multiple search algorithms",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
  
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Delivery Route Planning API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/api/docs",
            "health": "/api/v1/health",
            "generate_grid": "/api/v1/grid/generate",
            "search": "/api/v1/search",
            "compare_algorithms": "/api/v1/search/compare",
            "plan_deliveries": "/api/v1/delivery/plan"
        }
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "delivery-route-planner"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )