from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.services.exceptions import TeamAlreadyExistsError, TeamDoesNotExistError
from src.services.teams import TeamService

from .exceptions import BadRequestError, NotFoundError
from .schemas import ErrorCode, ErrorDetailSchema, ErrorResponseSchema, TeamMemberSchema, TeamSchema
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
async def add_team(request: TeamSchema, db: AsyncSession = Depends(get_db)) -> TeamSchema:
    service = TeamService(db)

    try:
        await service.create_team_with_members(request.team_name, request.members)
    except TeamAlreadyExistsError as e:
        raise BadRequestError(detail=ErrorDetailSchema(
            code=ErrorCode.TEAM_EXISTS,
            message='team_name already exists'
        )) from e

    return request


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
async def get_team(team_name: str, db: AsyncSession = Depends(get_db)) -> TeamSchema:
    team_service = TeamService(db)

    try:
        team_with_members = await team_service.get_team_with_members(team_name)
    except TeamDoesNotExistError as e:
        raise NotFoundError(
            detail=ErrorDetailSchema(
                code=ErrorCode.TEAM_DOES_NOT_EXIST,
                message=str(e)
            )
        ) from e

    return TeamSchema(
        team_name=team_with_members.team.name,
        members=[
            TeamMemberSchema(
                user_id=member.user_id,
                username=member.username,
                is_active=member.is_active
            ) for member in team_with_members.members
        ]
    )
