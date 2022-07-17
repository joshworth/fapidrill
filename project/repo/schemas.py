from typing import Union, List

from pydantic import BaseModel, Field, validator
import re


class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


class ItemCreate(ItemBase):
    pass


class ItemIndb(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str

    @validator("email")
    def validate_email(cls, value):
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex, value):
            raise ValueError("Invalid email address supplied.")
        return value


class UserCreate(UserBase):
    password: str


class UserIndb(UserBase):
    id: int
    is_active: bool
    items: List[ItemIndb] = []

    class Config:
        orm_mode = True
