"""Base domain error class."""


class DomainError(Exception):
    """Base exception for all domain errors.

    All business rule violations should inherit from this class.
    The rule_id links the error to the documented business rule.
    """

    def __init__(self, message: str, status: int):
        self.message = message
        self.status = status
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.status}] {self.message}"
