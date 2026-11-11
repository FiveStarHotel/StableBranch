from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=256)
    email: EmailStr

    model_config = {
        "str_strip_whitespace": True,
        "extra": "forbid",
    }

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v:
            raise ValueError("username не может быть пустым")
        if not v.replace("_", "").isalnum():
            raise ValueError("username: только буквы, цифры и _")
        return v.lower()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()

class UserWrite(UserBase):
    password: str = Field(min_length=8, max_length=128)

    def to_orm(self, hash_password: str) -> "User":
        from app.models.user import User
        return User(
            username=self.username,
            email=self.email,
            hash_password=hash_password,
        )

    def save(self, db: Session, hash_password: str) -> "User":
        user = self.to_orm(hash_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

class UserRead(UserBase):
    id: int = Field(gt=0)
    hash_password: str = Field(min_length=1, max_length=255)

    model_config = {
        "from_attributes": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
    }

    def to_json(self) -> dict:
        return self.model_dump(mode="json")

    @classmethod
    def from_orm_obj(cls, user) -> "UserRead":
        return cls.model_validate(user)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=256)
    email: EmailStr | None = None
    hash_password: str | None = Field(default=None, min_length=1, max_length=255)

    model_config = {
        "str_strip_whitespace": True,
        "extra": "forbid",
    }

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v:
            raise ValueError("username не может быть пустым")
        if not v.replace("_", "").isalnum():
            raise ValueError("username: только буквы, цифры и _")
        return v.lower()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str | None) -> str | None:
        return v.lower() if v is not None else v

    def apply(self, db: Session, user) -> "User":
        payload = self.model_dump(exclude_unset=True)
        for field, value in payload.items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user