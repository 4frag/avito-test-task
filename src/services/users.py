from src.db.models import User
from src.db.repositories.users import UserRepository
from src.db.repositories.teams import TeamRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.entities import UserWithTeamDTO
from sqlalchemy.exc import IntegrityError
from .exceptions import UserAlreadyExistsError, TeamDoesNotExistError


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.team_repo = TeamRepository(db)
    
    async def get_user_with_team(self, user_id: str) -> UserWithTeamDTO | None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        team = await self.team_repo.get_by_id(user.team_id)
        return UserWithTeamDTO(user=user, team=team)
    
    async def add_user(self, **kwargs) -> User:
        try:
            user = await self.user_repo.create(**kwargs)
        except IntegrityError as e:
            error_msg = str(e.orig).lower()
            print(error_msg)

            if 'insert or update on table "users" violates foreign key constraint "users_team_name_fkey"' in error_msg:
                raise TeamDoesNotExistError(kwargs['team_name'])
            raise UserAlreadyExistsError(kwargs['id'])
        return user
    
    async def bulk_add_users(self, users: list[dict]) -> list[User]:
        try:
            await self.user_repo.bulk_create(users)
        except IntegrityError as e:
            error_msg = str(e.orig).lower()

            if 'duplicate key value violates unique constraint "users_pkey"' in error_msg:
                already_created = await self.user_repo.filter_by(User.user_id.in_([user['user_id'] for user in users]))
                already_created_ids = [user.user_id for user in already_created]
                raise UserAlreadyExistsError(already_created_ids)
    
    async def update_user(self, **kwargs) -> User:
        try:
            user = await self.user_repo.update(**kwargs)
        except IntegrityError:
            raise UserAlreadyExistsError(kwargs['id'])
        return user