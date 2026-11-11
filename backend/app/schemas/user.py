from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=256)
    email: EmailStr

    model_config = {
        "str_strip_whitespace": True,
        "extra": "forbid"
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
    password: SecretStr = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    id: int = Field(gt=0)

    model_config = {
        "from_attributes": True,
        "str_strip_whitespace": True,
        "extra": "forbid"
    }


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=256)
    email: EmailStr | None = None
    password: SecretStr | None = Field(default=None, min_length=8, max_length=128)

    model_config = {
        "str_strip_whitespace": True,
        "extra": "forbid"
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