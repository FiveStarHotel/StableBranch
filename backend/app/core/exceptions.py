class AppError(Exception):
    status_code = 400
    detail = "Bad Request!"

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)
