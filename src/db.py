"""Database connection and utilities for PV Business Plan."""
import os
from typing import Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


def get_connection_string() -> str:
    """Build PostgreSQL connection string from environment variables."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME")

    if not all([user, password, database]):
        raise ValueError(
            "Missing required database environment variables. "
            "Check DB_USER, DB_PASSWORD, and DB_NAME in .env"
        )

    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"


def get_engine(echo: bool = False) -> Engine:
    """Create SQLAlchemy engine with connection pooling."""
    connection_string = get_connection_string()
    engine = create_engine(
        connection_string, echo=echo, pool_pre_ping=True, pool_size=5, max_overflow=10
    )
    return engine


_engine: Optional[Engine] = None


def get_shared_engine() -> Engine:
    """Get or create shared engine instance."""
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine


SessionLocal = sessionmaker(autocommit=False, autoflush=False)


@contextmanager
def get_session():
    """Context manager for database sessions."""
    engine = get_shared_engine()
    SessionLocal.configure(bind=engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_connection() -> bool:
    """Test database connection."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info("✓ Connected to PostgreSQL")
            logger.info(f"  Version: {version[:50]}...")

            result = conn.execute(
                text(
                    """SELECT table_name FROM information_schema.tables
                    WHERE table_schema='public'"""
                )
            )
            tables = [row[0] for row in result]
            logger.info(f"  Tables: {', '.join(tables) if tables else 'None'}")

            return True
    except Exception as e:
        logger.error(f"✗ Connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()
