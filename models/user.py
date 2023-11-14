from typing import Optional, List
from pydantic import BaseModel, Field

class UserModel(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    token: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)