from backend.app.database.models import User
from backend.app.schemas.user import UserRead


def who_am_i(user: User):
    return UserRead.model_validate(user)