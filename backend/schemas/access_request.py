from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AccessRequestCreate(BaseModel):
    requested_role: Optional[str] = None
    requested_page: Optional[str] = None
    message: Optional[str] = None

class AccessRequestOut(BaseModel):
    id: int
    user_id: int
    username: str
    requested_role: Optional[str]
    requested_page: Optional[str]
    message: Optional[str]
    status: str
    created_at: datetime

    class Config:
        orm_mode = True 