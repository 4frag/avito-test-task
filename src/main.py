from typing import Any
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.api import teams, users
from src.db.database import get_db_connection, init_db, stop_db
from src.schemas.base import ErrorResponseSchema


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any, Any]:
    print('Application started')
    app.state.db_pool, app.state.db_engine  = await init_db()
    # app.state.db_pool = await init_db()
    yield

    if app.state.db_engine:
        await stop_db(app.state.db_engine)
        # await stop_db(app.state.db_pool)
    print('Application stopped')


async def httpexception_handler(_request: Request, exc: type[HTTPException]) -> JSONResponse:
    content = ErrorResponseSchema(error=exc.detail).model_dump()
    return JSONResponse(content=content, status_code=exc.status_code)


app = FastAPI(lifespan=lifespan)
app.add_exception_handler(HTTPException, httpexception_handler)

app.include_router(users.router)
app.include_router(teams.router)
# app.include_router(pull_requests.router)


@app.get('/health')
async def health_check(conn: AsyncSession = Depends(get_db_connection)) -> dict:
    await conn.execute(text('SELECT 1'))
    return {'status': 'healthy'}
