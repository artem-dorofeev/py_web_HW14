from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date

from pydantic_settings import SettingsConfigDict


class ContactModel(BaseModel):

    name: str = Field(min_length=2, max_length=20)
    surname: str = Field(min_length=2, max_length=20)
    email: str = EmailStr 
    phone: str = Field(min_length=2, max_length=20)
    birthday: date
    additional: str = Field()
    

class ResponseContact(BaseModel):
    model_config = SettingsConfigDict(from_attributes=True)
    id: int = 1
    name: str
    surname: str
    email: str = EmailStr
    phone: str
    birthday: date
    additional: str 
    created_at: datetime
    updated_at: datetime



class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr