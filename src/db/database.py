import os
from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.db.exceptions import DatabaseURLIsNotProvidedError


DATABASE_URL = os.getenv('DATABASE_URL', None)
if not DATABASE_URL:
    raise DatabaseURLIsNotProvidedError

# engine = create_async_engine(
#     DATABASE_URL,
#     poolclass=AsyncAdaptedQueuePool,
#     pool_pre_ping=True,
#     pool_size=20
# )
# session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

# async def get_db() -> AsyncGenerator[AsyncSession]:
#     if not session_factory:
#         raise Exception

#     async with session_factory() as session:
#         yield session


# async def init_db() -> asyncpg.Pool:
#     engine = create_async_engine(
#         DATABASE_URL,
#         pool_size=5,
#         max_overflow=10,
#         # echo=True
#     )

#     return async_sessionmaker(
#         engine,
#         expire_on_commit=False,
#         class_=AsyncSession
#     ), engine
# async def init_db() -> asyncpg.Pool:
#     return asyncpg.create_pool(
#         dsn=DATABASE_URL,
#         min_size=1,
#         max_size=10,
#         max_inactive_connection_lifetime=300,
#         command_timeout=60,
#     )


# async def stop_db(engine: AsyncEngine) -> None:
#     await engine.dispose()
# async def stop_db(pool) -> None:
#     await pool.close()


# async def get_db_connection(request: Request) -> AsyncIterator[AsyncSession]:
#     async with request.app.state.db_pool() as session:
#         try:
#             yield session
#             await session.commit()
#         except Exception:
#             await session.rollback()
#             raise
#         finally:
#             await session.close()
# async def get_db_connection(request: Request) -> AsyncIterator[asyncpg.Connection]:
#     pool = request.app.state.db_pool
#     async with pool.acquire() as connection:
#         try:
#             yield connection
#         finally:
#             pass


async def init_db() -> tuple[AsyncSession, AsyncEngine]:
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        pool_size=20,
        max_overflow=40,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    return session_factory, engine

async def stop_db(engine: AsyncEngine) -> None:
    await engine.dispose()

async def get_db_connection(request: Request) -> AsyncIterator[AsyncSession]:
    async_session = request.app.state.db_pool
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
