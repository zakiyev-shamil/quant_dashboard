"""
QuantLab Lite — Database Connection

PostgreSQL connection management via SQLAlchemy.
The user creates the database and runs db_schema.sql manually.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

from app.core.config import DATABASE_URL

# ---------------------------------------------------------------------------
# Engine (singleton pattern via module-level variable)
# ---------------------------------------------------------------------------
_engine: Engine | None = None


def get_engine() -> Engine:
    """
    Get or create the SQLAlchemy engine.

    Uses connection pooling with sensible defaults for a quant workload:
    - pool_size=5: number of persistent connections
    - max_overflow=10: extra connections if pool is exhausted
    - pool_pre_ping=True: verify connections before use
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False,
        )
    return _engine


def get_session() -> Session:
    """Create a new database session."""
    engine = get_engine()
    session_factory = sessionmaker(bind=engine)
    return session_factory()


def dispose_engine() -> None:
    """Dispose of the engine and close all connections. Useful for testing."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
