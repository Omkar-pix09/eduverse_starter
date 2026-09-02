from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileUpdate(BaseModel):
    github_username: Optional[str] = None
    leetcode_username: Optional[str] = None
    cgpa: Optional[float] = None
    branch: Optional[str] = None
    grad_year: Optional[int] = None
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None


class ChatRequest(BaseModel):
    message: str
