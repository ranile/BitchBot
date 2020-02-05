class DatabaseError(Exception):
    pass


class NotFound(DatabaseError):
    pass
