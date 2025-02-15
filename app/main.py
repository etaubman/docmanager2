"""
Path: app/main.py
Description: Main FastAPI application entry point
Purpose: Configures and starts the FastAPI application with all routes and middleware
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import document_routes

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Manager API",
    description="A REST API for managing documents with CRUD operations",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with prefix
app.include_router(document_routes.router, prefix="/api")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")