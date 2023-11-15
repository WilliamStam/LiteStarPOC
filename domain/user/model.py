from typing import Optional, List
from pydantic import BaseModel, Field

class UserModel(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    token: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    
    def has_permissions(self, scopes:List[str] = None):
        if scopes is None:
            scopes = []
        
        for scope in scopes:
            if str(scope) not in self.permissions:
                return False
            
        return True