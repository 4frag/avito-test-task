from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum


# Enums
class ErrorCode(str, Enum):
    TEAM_EXISTS = "TEAM_EXISTS"
    TEAM_DOES_NOT_EXIST = "TEAM_DOES_NOT_EXIST"
    PR_EXISTS = "PR_EXISTS"
    USER_EXISTS = "USER_EXISTS"
    PR_MERGED = "PR_MERGED"
    NOT_ASSIGNED = "NOT_ASSIGNED"
    NO_CANDIDATE = "NO_CANDIDATE"
    NOT_FOUND = "NOT_FOUND"


class PRStatus(str, Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"


# Error Schemas
class ErrorDetailSchema(BaseModel):
    code: ErrorCode
    message: str


class ErrorResponseSchema(BaseModel):
    error: ErrorDetailSchema

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "resource not found"
                }
            }
        }


# Team Schemas
class TeamMemberSchema(BaseModel):
    user_id: str
    username: str
    is_active: bool


class TeamSchema(BaseModel):
    team_name: str
    members: List[TeamMemberSchema]


# User Schemas
class UserSchema(BaseModel):
    user_id: str
    username: str
    is_active: bool
    team_name: str

    class Config:
        populate_by_name = True


# Pull Request Schemas
class PullRequestShortSchema(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus


class PullRequest(PullRequestShortSchema):
    assigned_reviewers: List[str]
    created_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None


# Requests schemas
class UserSetActiveRequestSchema(BaseModel):
    user_id: str
    is_active: bool

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "u2",
                "is_active": False
            }
        }