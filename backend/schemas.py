from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Base Pydantic models
class QueryBase(BaseModel):
    topic: str

class DocumentBase(BaseModel):
    filename: str
    content: Optional[str] = None
    response: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

# Create models
class QueryCreate(QueryBase):
    pass

class DocumentCreate(DocumentBase):
    pass

class UserCreate(UserBase):
    password: str

# Google authentication schemas
class GoogleUserInfo(BaseModel):
    google_id: str
    email: EmailStr
    full_name: Optional[str] = None
    picture: Optional[str] = None

class GoogleAuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserBase

# Read models
class Query(QueryBase):
    id: int
    response: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Document(DocumentBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    disabled: bool
    created_at: datetime
    picture: Optional[str] = None
    queries: List[Query] = []
    documents: List[Document] = []

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 