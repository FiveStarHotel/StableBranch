import unicodedata

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator


class UserBase(BaseModel):
    username: str = Field(min_length=4, max_length=256)
    email: EmailStr

    model_config = {
        "str_strip_whitespace": True,
        "extra": "forbid",
    }

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = unicodedata.normalize("NFC", v)
        if not all(ch.isalnum() or ch == "_" for ch in v):
            raise ValueError("username: только буквы, цифры и _")
        return v

class UserCreate(UserBase):
    password: SecretStr = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    id: int = Field(gt=0)

    model_config = {
        "from_attributes": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
    }

class UserProfileUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=4, max_length=256)

    model_config = {"str_strip_whitespace": True, "extra": "forbid"}

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = unicodedata.normalize("NFC", v)
        if not all(ch.isalnum() or ch == "_" for ch in v):
            raise ValueError("username: только буквы, цифры и _")
        return v

class PasswordChange(BaseModel):
    old_password: SecretStr = Field(min_length=8, max_length=128)
    new_password: SecretStr = Field(min_length=8, max_length=128)

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetVerifyCode(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")

class PasswordResetComplete(BaseModel):
    reset_token: str
    new_password: SecretStr = Field(min_length=8, max_length=128)

class RegisterConfirm(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")

class EmailChange(BaseModel):
    old_email: EmailStr
    new_email: EmailStr

class EmailChangeConfirm(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")