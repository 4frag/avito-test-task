from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from src.db.database import get_db
from src.services.exceptions import UserAlreadyExistsError, TeamDoesNotExistError, TeamAlreadyExistsError
from src.services.teams import TeamService
from .tags import APITags
from .schemas import TeamSchema, ErrorResponseSchema, ErrorDetailSchema, ErrorCode, TeamMemberSchema


router = APIRouter(prefix='/teams', tags=[APITags.TEAMS])


@router.post('/add', response_model=TeamSchema)
async def add_team(request: TeamSchema, db = Depends(get_db)):
    service = TeamService(db)

    try:
        await service.create_team_with_members(request.team_name, request.members)
    except TeamAlreadyExistsError as e:
        response = ErrorResponseSchema(error=ErrorDetailSchema(
            code=ErrorCode.TEAM_EXISTS,
            message=str(e)
        )).model_dump()
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=response
        )
    except UserAlreadyExistsError as e:
        response = ErrorResponseSchema(error=ErrorDetailSchema(
            code=ErrorCode.USER_EXISTS,
            message=str(e)
        )).model_dump()
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=response
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=request.model_dump()
    )


@router.get('/get', response_model=TeamSchema)
async def get_team(team_name: str, db = Depends(get_db)):
    team_service = TeamService(db)

    try:
        team_with_members = await team_service.get_team_with_members(team_name)
    except TeamDoesNotExistError:
        response = ErrorResponseSchema(error=ErrorDetailSchema(
            code=ErrorCode.TEAM_DOES_NOT_EXIST,
            message=f'Team with name {team_name} does not exist'
        )).model_dump()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response
        )

    response = TeamSchema(
        team_name=team_with_members.team.name,
        members=[TeamMemberSchema(user_id=member.user_id, username=member.username, is_active=member.is_active) for member in team_with_members.members]
    ).model_dump()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response
    )
