class UnauthorizedObjectAccessError(Exception):
    """Raised when a user tries to access an object not owned by them.
    """

class ObjectNotFoundError(Exception):
    """Raised when the requested object is not found.
    """

