from fastapi import status


class AppError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad Request!"

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class UsernameOrEmailOccupiedError(AppError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Username or email is occupied!"


class InvalidVerificationCodeError(AppError):
    detail = "Invalid or expired code!"


class TooManyVerificationAttemptsError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Too many attempts, registration failed. Register again."


class TooManyAccountVerificationAttemptsError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Too many verification attempts."


class CredentialsError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid username, email or password!"


class InvalidRefreshTokenError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid refresh token!"


class InactiveUserError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "User is inactive!"


class InvalidAccessToken(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid access token!"
