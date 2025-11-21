import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (AsyncSession, async_scoped_session,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Conditionally import the Base class based on USE_SUPABASE setting
use_supabase = os.getenv("USE_SUPABASE", "false").lower() == "true"

if use_supabase:
    # Import Base from models_supabase when using Supabase
    from .models_supabase import Base
else:
    # Import Base from models for local development
    from .models import Base

# Database configuration
TESTING = os.getenv("TESTING", "False").lower() in ("true", "1", "t")

if TESTING:
    # Use SQLite for testing
    DATABASE_URL = "sqlite+aiosqlite:///./test.db"
    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True,
        poolclass=NullPool,
    )
else:
    # Supabase PostgreSQL configuration
    DB_USER = os.getenv("POSTGRES_USER", "postgres")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
    DB_HOST = os.getenv(
        "POSTGRES_HOST", "db.xxx.supabase.co"
    )  # Your Supabase database host
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DB", "postgres")

    # Construct DATABASE_URL with SSL for Supabase
    DATABASE_URL = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Configure engine with SSL for Supabase
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,  # Enable SQL query logging
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
        connect_args={"ssl": "prefer", "sslmode": "require"},
    )

# Create async session factory with scoped sessions for better handling in async context
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create a scoped session for better handling in async context
AsyncScopedSession = async_scoped_session(
    async_session_factory, scopefunc=asyncio.current_task
)

# Synchronous session for backward compatibility
# (Use with caution - prefer async operations)
sync_engine = create_async_engine(DATABASE_URL, echo=False)
sync_session_factory = sessionmaker(
    bind=sync_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


# Dependency to get database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields database sessions.
    Handles session lifecycle including commit/rollback and closing.
    """
    session = AsyncScopedSession()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()


async def create_tables():
    """
    Create all database tables.
    Should be called on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """
    Drop all database tables.
    Use with caution - only for testing/development!
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Helper function to get a database session
def get_db_session() -> AsyncSession:
    """
    Get a database session for use in non-FastAPI contexts.
    Remember to close the session when done.
    """
    return AsyncScopedSession()
