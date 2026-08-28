from typing import Annotated
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserBase(BaseModel):
    username: Annotated[str, Field(min_length=1, max_length=50)]
    email: Annotated[EmailStr, Field(max_length=120)]
    
class UserCreate(UserBase):
    pass
    
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    image_file: str | None
    image_path: str
    
        
class PostBase(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=100)]
    content: Annotated[str, Field(min_length=1)]

class PostCreate(PostBase):
    user_id: int # temp
    
class PostUpdate(BaseModel):
    title: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    content: Annotated[str | None, Field(min_length=1)] = None

class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse