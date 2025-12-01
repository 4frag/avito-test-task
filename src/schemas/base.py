from pydantic import BaseModel

from type_defs import ErrorCode


# Error Schemas
class ErrorDetailSchema(BaseModel):
    code: ErrorCode
    message: str


class ErrorResponseSchema(BaseModel):
    error: ErrorDetailSchema

    class Config:
        json_schema_extra = {
            'example': {
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'resource not found'
                }
            }
        }
