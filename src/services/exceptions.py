class UserAlreadyExistsError(Exception):
    def __init__(self, user_id: str | list[str]) -> None:
        if isinstance(user_id, str):
            super().__init__(f'User with id {user_id} already exists')
        else:
            super().__init__(f"Users with id {', '.join(user_id)} already exists")


class UserDoesNotExistError(Exception):
    def __init__(self, user_id: str) -> None:
        super().__init__(f'User with id {user_id} does not exist')


class UserIsNotActiveError(Exception):
    def __init__(self, user_id: str) -> None:
        super().__init__(f'User with id {user_id} is not active')


class TeamDoesNotExistError(Exception):
    def __init__(self, team_name: str) -> None:
        super().__init__(f'Team with name {team_name} does not exist')


class TeamAlreadyExistsError(Exception):
    def __init__(self, team_name: str) -> None:
        super().__init__(f'Team with name {team_name} already exists')


class PRDoesNotExistError(Exception):
    def __init__(self, pr_id: str) -> None:
        super().__init__(f'PR with id {pr_id} does not exist')


class PRNotModifiableError(Exception):
    def __init__(self) -> None:
        super().__init__('Cannot change reviewers on merged PR')


class ReviewerNotAssignedError(Exception):
    def __init__(self, reviewer_id: str, pr_id: str) -> None:
        super().__init__(f'User {reviewer_id} is not assigned to PR {pr_id}')


class AuthorCannotBeAReviewerError(Exception):
    def __init__(self) -> None:
        super().__init__('Cannot assign PR author as reviewer')


class ReviewerFromWrongTeamError(Exception):
    def __init__(self, reviewer_id: str) -> None:
        super().__init__(f'Reviewer {reviewer_id} must be from the same team as the author of pull request')


class CannotAssignMoreReviewersError(Exception):
    def __init__(self, max_reviewers_count: int) -> None:
        super().__init__(f'Cannot assign more than {max_reviewers_count} reviewers')


class PRAlreadyExistsError(Exception):
    def __init__(self, pr_id: str) -> None:
        super().__init__(f'PR with id {pr_id} already exists')
