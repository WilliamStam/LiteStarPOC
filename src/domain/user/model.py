from typing import Optional, List
from pydantic import BaseModel, Field

class UserModel(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    token: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    
    def has_permissions(self, permissions:List[str] = None):
        if permissions is None:
            permissions = []
        
        for permission in permissions:
            if str(permission) not in self.permissions:
                return False
            
        return True