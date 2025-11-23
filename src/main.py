from typing import Any
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.api import pull_requests, teams, users
from src.api.schemas import ErrorResponseSchema
from src.db.database import engine, get_db
from src.exceptions import CannotConnectToDatabaseError


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[Any, Any, Any]:
    print('Application started')
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        print('Database connection verified')
    except Exception as e:
        raise CannotConnectToDatabaseError from e
    yield
    await engine.dispose()
    print('Application stopped')


async def httpexception_handler(_request: Request, exc: type[HTTPException]) -> JSONResponse:
    content = ErrorResponseSchema(error=exc.detail).model_dump()
    return JSONResponse(content=content, status_code=exc.status_code)


app = FastAPI(lifespan=lifespan)
app.add_exception_handler(HTTPException, httpexception_handler)

app.include_router(users.router)
app.include_router(teams.router)
app.include_router(pull_requests.router)


@app.get('/health')
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    await db.execute(text('SELECT 1'))
    return {'status': 'healthy'}
