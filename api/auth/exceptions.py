"""Authentication and authorization exceptions."""


class AuthenticationError(Exception):
    """Base exception for authentication errors."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Exception raised when credentials are invalid."""
    pass


class InvalidTokenError(AuthenticationError):
    """Exception raised when a token is invalid."""
    pass


class ExpiredTokenError(AuthenticationError):
    """Exception raised when a token has expired."""
    pass


class TokenRevokedError(AuthenticationError):
    """Exception raised when a token has been revoked."""
    pass


class InsufficientPermissionError(AuthenticationError):
    """Exception raised when user lacks required permission."""
    pass


class UserNotFoundError(AuthenticationError):
    """Exception raised when a user is not found."""
    pass


class UserDisabledError(AuthenticationError):
    """Exception raised when a user account is disabled."""
    pass


class PasswordValidationError(AuthenticationError):
    """Exception raised when password validation fails."""
    pass
