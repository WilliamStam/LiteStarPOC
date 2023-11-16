import dataclasses
from typing import Union
from .collection import Collection

@dataclasses.dataclass
class Permission():
    
    key: str
    description: str = None
    parent: Union['Permission', None] = None
    
    def __repr__(self):
        return self.id
    
    @property
    def id(self) -> str:
        p = []
        p.append(self.key)
        parent = self.parent
        while parent:
            if parent:
                p.append(parent.key)
            parent = parent.parent
        p.reverse()
        return str(".".join(p))
    

    
class PermissionCollection(Collection[Permission]):
    def add(self, item: Permission):
        super().add(item)