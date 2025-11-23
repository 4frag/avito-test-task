from abc import ABC
from typing import Optional, TypeVar, Generic, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
        self._pk_field_name = self._get_pk_field_name()
    
    def _get_pk_field_name(self) -> str:
        """Определяет имя поля первичного ключа"""
        pk_columns = [column for column in self.model.__table__.columns if column.primary_key]
        
        if not pk_columns:
            raise ValueError(f"Model {self.model.__name__} has no primary key")
        
        if len(pk_columns) > 1:
            raise ValueError(f"Model {self.model.__name__} has composite primary key")
        
        return pk_columns[0].name

    async def get_by_pk(self, value: str) -> Optional[ModelType]:
        result = await self.db.execute(
            select(self.model).where(getattr(self.model, self._pk_field_name) == value)
        )
        return result.scalar_one_or_none()
    
    async def get_by(self, **filters) -> Optional[ModelType]:
        if not filters:
            return None
        
        result = await self.db.execute(
            select(self.model).filter_by(**filters)
        )
        return result.scalar_one_or_none()
    
    async def filter_by(self, *filters) -> list[ModelType]:
        if not filters:
            return await self.get_all()
        
        query = select(self.model).where(*filters)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_all(self) -> list[ModelType]:
        result = await self.db.execute(select(self.model))
        return result.scalars().all()

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        return instance
    
    async def bulk_create(self, objects_data: list[dict]) -> list[ModelType]:
        try:
            instances = [self.model(**data) for data in objects_data]
            self.db.add_all(instances)
            
            # for instance in instances:
            #     await self.db.refresh(instance)
            
            return instances
        except IntegrityError as e:
            await self.db.rollback()
            if hasattr(e, 'params') and e.params:
                # e.params содержит список параметров которые пытались вставить
                conflicting_params = e.params
                print(f"Conflicting parameters: {conflicting_params}")
                
                # Находим ID конфликтующего пользователя
                for params in conflicting_params:
                    if 'user_id' in params:
                        print(f"Duplicate user_id: {params['user_id']}")
            
            raise

    async def update(self, id: str, **kwargs) -> Optional[ModelType]:
        instance = await self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
        return instance

    async def delete(self, id: str) -> bool:
        instance = await self.get_by_id(id)
        if instance:
            await self.db.delete(instance)
            return True
        return False