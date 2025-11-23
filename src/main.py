from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.exceptions import CannotConnectToDatabaseError
from src.db.database import get_db, engine
from src.api import users, teams


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application started")
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("Database connection verified")
    except Exception as e:
        raise CannotConnectToDatabaseError from e
    yield
    await engine.dispose()
    print("Application stopped")


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(teams.router)


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "healthy"}
