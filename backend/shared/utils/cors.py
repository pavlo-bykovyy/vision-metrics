"""
shared/middlewares/cors.py

This module handles Cross-Origin Resource Sharing (CORS) middleware configuration 
for FastAPI applications.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI) -> None:
    """
    Configures and adds CORS middleware to the FastAPI application.
    Allows all origins, credentials, methods, and headers for development purposes.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )