class CannotConnectToDatabaseError(Exception):
    def __init__(self) -> None:
        super().__init__('Cannot connect to database')
