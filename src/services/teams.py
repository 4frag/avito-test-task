from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import TeamMemberSchema
from src.db.models import User
from src.db.repositories.teams import TeamRepository
from src.db.repositories.users import UserRepository
from src.entities import TeamWithMembers

from .exceptions import TeamAlreadyExistsError, TeamDoesNotExistError


class TeamService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.team_repo = TeamRepository(db)

    async def get_team_with_members(self, team_name: str) -> TeamWithMembers:
        team = await self.team_repo.get_by_pk(team_name)
        if not team:
            raise TeamDoesNotExistError(team_name)

        members = await self.user_repo.filter_by(User.team_name == team_name)

        return TeamWithMembers(team, members)

    async def create_team_with_members(self, team_name: str, members: list[TeamMemberSchema]) -> TeamWithMembers:
        '''
        Создает команду с пользователями.

        Если пользователи с указанными user_id уже существовали - обновляет их
        '''
        try:
            team = await self.team_repo.create(name=team_name)
            upsert_data = [{**member.model_dump(), 'team_name': team.name} for member in members]
            users = await self.user_repo.upsert(upsert_data)
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            error_msg = str(e.orig).lower()

            if 'duplicate key value violates unique constraint "teams_pkey"' in error_msg:
                raise TeamAlreadyExistsError(team_name) from e
            raise
        else:
            return TeamWithMembers(team=team, members=users)

