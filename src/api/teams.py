from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db_connection
from src.schemas.base import ErrorDetailSchema, ErrorResponseSchema
from src.schemas.teams import TeamSchema
from src.services.exceptions import TeamAlreadyExistsError
from src.services.teams import TeamService
from type_defs import ErrorCode

from .exceptions import BadRequestError, NotFoundError
from .tags import APITags


router = APIRouter(prefix='/teams', tags=[APITags.TEAMS])


@router.post(
    '/add',
    summary='Создать команду с участниками (создаёт/обновляет пользователей)',  # noqa: RUF001
    responses={
        400: {
            'model': ErrorResponseSchema,
            'description': 'Team with name query_params.team_name already exists'
        }
    }
)
async def add_team(request: TeamSchema, db: AsyncSession = Depends(get_db_connection)) -> TeamSchema:
    try:
        team = await TeamService(db).create_team_with_members(request)
    except TeamAlreadyExistsError as e:
        raise BadRequestError(detail=ErrorDetailSchema(
            code=ErrorCode.TEAM_EXISTS,
            message='team_name already exists'
        )) from e
    return TeamSchema.model_validate(team)


@router.get(
    '/get',
    summary='Получить команду с участниками',  # noqa: RUF001
    responses={
        404: {
            'model': ErrorResponseSchema,
            'description': 'Team not found'
        }
    }
)
async def get_team(team_name: str, db: AsyncSession = Depends(get_db_connection)) -> TeamSchema:
    team = await TeamService(db).get_team_with_members(team_name)
    if team is None:
        raise NotFoundError(
            detail=ErrorDetailSchema(
                code=ErrorCode.TEAM_DOES_NOT_EXIST,
                message=f'Team {team_name} does not exist'
            )
        )
    return TeamSchema.model_validate(team)
