class DomainException(Exception):
    """Base exception for domain errors"""

    pass


class DomainValidationError(DomainException):
    """Exception raised for domain validation errors"""

    pass


class EntityNotFoundError(DomainException):
    """Exception raised when an entity is not found"""

    pass
