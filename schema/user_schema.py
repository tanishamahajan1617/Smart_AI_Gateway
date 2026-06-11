from pydantic import BaseModel
from typing import Optional


from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None


class UserResponse(BaseModel):
    user_id: str
    email: EmailStr
    username: str        

class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)