from pydantic import BaseModel, ConfigDict

from .pull_requests import PullRequestShortSchema


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    username: str
    is_active: bool
    team_name: str


class UserSetActiveRequestSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'user_id': 'u2',
                'is_active': False
            }
        }
    )
    user_id: str
    is_active: bool


class UserGetReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    pull_requests: list[PullRequestShortSchema]
