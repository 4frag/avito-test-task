class DatabaseURLIsNotProvidedError(Exception):
    def __init__(self):
        super().__init__('You should provide DATABASE_URL environment variable to start this application')