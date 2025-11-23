from enum import Enum


class ErrorCode(str, Enum):
    TEAM_EXISTS = 'TEAM_EXISTS'
    TEAM_DOES_NOT_EXIST = 'TEAM_DOES_NOT_EXIST'
    PR_EXISTS = 'PR_EXISTS'
    USER_EXISTS = 'USER_EXISTS'
    PR_MERGED = 'PR_MERGED'
    NOT_ASSIGNED = 'NOT_ASSIGNED'
    NO_CANDIDATE = 'NO_CANDIDATE'
    NOT_FOUND = 'NOT_FOUND'


class PRStatus(str, Enum):
    OPEN = 'OPEN'
    MERGED = 'MERGED'
