from dataclasses import dataclass
from src.db.models import User, Team


@dataclass
class UserWithTeamDTO:
    user: User
    team: Team


@dataclass
class TeamWithMembers:
    team: Team
    members: list[User]
