from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os

from src.db.exceptions import DatabaseURLIsNotProvidedError

DATABASE_URL = os.getenv("DATABASE_URL", None)
if not DATABASE_URL:
    raise DatabaseURLIsNotProvidedError

engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()