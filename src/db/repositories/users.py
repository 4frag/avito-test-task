from src.db.models import User

from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User
