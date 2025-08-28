from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)
from core import settings
from .models import Base


class DatabaseHelper:
    """
    Helper class to manage async SQLAlchemy database connections and sessions.

    Provides:
    - Async engine creation
    - Async session factory
    - Database initialization
    - Session context manager for dependency injection
    """

    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        """
        Initialize the database helper with an async engine and sessionmaker.

        Args:
            url (str): Database connection URL
            echo (bool): Log all SQL queries (default False)
            echo_pool (bool): Log connection pool actions (default False)
            pool_size (int): Size of the connection pool (default 5)
            max_overflow (int): Extra connections allowed beyond pool_size (default 10)
        """
        # Create the asynchronous engine
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        # Create async session factory
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,  # Don't automatically flush on query
            autocommit=False,  # Manage commits manually
            expire_on_commit=False,  # Keep objects usable after commit
        )

    async def init_db(self):
        """
        Initialize the database by creating all tables based on Base metadata.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        """
        Dispose of the async engine and close all connections.
        """
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Async context manager for providing a session.

        Usage:
            async for session in db_helper.session_getter():
                ...
        """
        async with self.session_factory() as session:
            yield session


# -----------------------------
# Global database helper instance
# -----------------------------
db_helper = DatabaseHelper(
    url=settings.db.url,
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)
