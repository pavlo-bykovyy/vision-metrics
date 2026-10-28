"""
database.py

This module sets up the database connection using SQLAlchemy.
It reads database credentials from environment variables and provides
a session generator for dependency injection.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Fetching database credentials from environment variables.
# Using defaults just in case they are not set.
DB_USER = os.getenv("DB_USERNAME", "admin")
DB_PASS = os.getenv("DB_PASSWORD", "superpassword")
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "visionmetrics_db")

# 2. Building the connection string for PostgreSQL.
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"

# 3. Creating the database engine.
# pool_pre_ping=True ensures the connection is valid before running a query,
# which prevents errors if the database connection temporarily drops.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)

# 4. Creating a configured "SessionLocal" class.
# Each instance of this class will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Creating a base class for our database models.
# All models (like User, Dataset, etc.) will inherit from this Base.
Base = declarative_base()

def get_db():
    """
    Creates and yields a new database session.
    Ensures that the session is closed safely after the request is finished.

    Yields:
        Session: A SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()