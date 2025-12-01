from pydantic import BaseModel, ConfigDict


class TeamMemberSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    username: str
    is_active: bool


class TeamSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    members: list[TeamMemberSchema]
