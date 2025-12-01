from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import attributes

from src.db.models import Team
from src.db.repositories.teams import TeamRepository
from src.db.repositories.users import UserRepository
from src.schemas.teams import TeamSchema

from .exceptions import TeamAlreadyExistsError


class TeamService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.team_repo = TeamRepository(db)

    async def get_team_with_members(self, team_name: str) -> Team | None:
        return await self.team_repo.get_where(
            Team.name == team_name,
            join_=[Team.members]
        )

    async def create_team_with_members(self, request: TeamSchema) -> Team:
        '''
        Создает команду с пользователями.

        Если пользователи с указанными user_id уже существовали - обновляет их
        '''
        try:
            team = await self.team_repo.create(name=request.name)
        except IntegrityError as e:
            await self.db.rollback()
            error_msg = str(e.orig).lower()

            if 'duplicate key value violates unique constraint "teams_pkey"' in error_msg:
                raise TeamAlreadyExistsError(request.name) from e
            raise
        else:
            upsert_data = [{**member.model_dump(), 'team_name': request.name} for member in request.members]
            users = await self.user_repo.upsert(upsert_data)
            attributes.set_committed_value(team, 'members', users)
            await self.db.commit()
            return team
