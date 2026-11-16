from fastapi import status


class AppError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad Request!"

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)
