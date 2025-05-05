from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class UserBase(BaseModel):
    name: str
    surname: str
    email: str
    password: str


class UserCreate(UserBase):
    pass


class AuthenticatedUser(BaseModel):
    email: str
    id: int
    name: str
    surname: str


class AuthorizationTokens(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    refresh_token_expires_in: int
