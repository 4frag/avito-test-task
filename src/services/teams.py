from src.db.models import User
from src.db.repositories.users import UserRepository
from src.db.repositories.teams import TeamRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.entities import TeamWithMembers
from src.api.schemas import TeamMemberSchema
from .exceptions import TeamDoesNotExistError, UserAlreadyExistsError, TeamAlreadyExistsError
from sqlalchemy.exc import IntegrityError


class TeamService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.team_repo = TeamRepository(db)

    async def get_team_with_members(self, team_name: str) -> TeamWithMembers:
        team = await self.team_repo.get_by_pk(team_name)
        if not team:
            raise TeamDoesNotExistError

        members = await self.user_repo.filter_by(User.team_name == team_name)

        return TeamWithMembers(team, members)
    
    async def create_team_with_members(self, team_name: str, members: list[TeamMemberSchema]) -> TeamWithMembers:
        try:
            team = await self.team_repo.create(name=team_name)
            members_d = [{'team_name': team.name, **member.model_dump()} for member in members]
            await self.user_repo.bulk_create(members_d)
            await self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig).lower()

            if 'duplicate key value violates unique constraint "teams_pkey"' in error_msg:
                raise TeamAlreadyExistsError(team_name)
            elif 'duplicate key value violates unique constraint "users_pkey"' in error_msg:
                raise UserAlreadyExistsError([member.user_id for member in members])
            raise
