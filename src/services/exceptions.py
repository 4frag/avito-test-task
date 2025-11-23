class UserAlreadyExistsError(Exception):
    def __init__(self, user_id: str | list[str]): 
        if isinstance(user_id, str):
            super().__init__(f"User with id {user_id} already exists")
        else:
            super().__init__(f"Users with id {', '.join(user_id)} already exists")


class TeamDoesNotExistError(Exception):
    def __init__(self, team_name):
        super().__init__(f"Team with name {team_name} does not exist")


class TeamAlreadyExistsError(Exception):
    def __init__(self, team_name):
        super().__init__(f"Team with name {team_name} already exists")
