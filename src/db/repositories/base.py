from typing import Generic, TypeVar
from abc import ABC

from sqlalchemy import inspect, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.db.models import Base


ModelType = TypeVar('ModelType', bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_where(self, *conditions: list, join_: list | None = None) -> ModelType:
        if not conditions:
            return None

        stmt = select(self.model) \
            .where(*conditions)
        if join_ is not None:
            stmt = stmt.options(joinedload(*join_))
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_where(self, *conditions: list, join_: list | None = None) -> list[ModelType]:
        if not conditions:
            return await self.get_all()

        stmt = select(self.model) \
            .where(*conditions)
        if join_ is not None:
            stmt = stmt.options(joinedload(*join_))
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_all(self, join_: list | None = None) -> list[ModelType]:
        if join_ is None:
            join_ = []

        stmt = select(self.model) \
            .options(joinedload(*join_))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs: dict) -> ModelType:
        stmt = insert(self.model).values(**kwargs).returning(self.model)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def update_one(self, *where_cond: list, **update_fields: dict) -> ModelType:
        stmt = update(self.model).where(*where_cond).values(**update_fields).returning(self.model)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def update(self, *where_cond: list, **update_fields: dict) -> list[ModelType]:
        stmt = update(self.model).where(*where_cond).values(**update_fields)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def upsert(self, instances: list[dict]) -> list[ModelType]:
        if not instances:
            return []

        conflict_columns = [
            col.name
            for col in inspect(self.model).columns
            if col.unique or col.primary_key
        ]

        stmt = insert(self.model).values(instances)
        stmt = stmt.on_conflict_do_update(
            index_elements=conflict_columns,
            set_={
                field: getattr(stmt.excluded, field)
                for field in instances[0]
            }
        ).returning(self.model)

        result = await self.db.execute(stmt)
        return result.scalars().all()
