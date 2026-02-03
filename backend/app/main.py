"""
Air Quality Dashboard - Backend API
FastAPI application for serving air quality data
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database import engine, create_tables, load_sample_data
from app.routers import air_quality, stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    logger.info("Starting up... Creating database tables")
    create_tables()
    load_sample_data()
    logger.info("Database initialized successfully")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Air Quality API",
    description="API REST pour les données de qualité de l'air en France",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(air_quality.router, prefix="/api/v1", tags=["Air Quality"])
app.include_router(stats.router, prefix="/api/v1", tags=["Statistics"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Air Quality Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Kubernetes probes"""
    return {
        "status": "healthy",
        "service": "air-quality-api",
        "version": "1.0.0"
    }
