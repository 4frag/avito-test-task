class CannotConnectToDatabaseError(Exception):
    def __init__(self):
        super().__init__('Cannot connect to database')