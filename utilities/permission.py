import dataclasses
from typing import Union


@dataclasses.dataclass
class Permission():
    """

    Class Permission

    Represents a permission in a system.

    Attributes:
        key (str): The unique key identifying the permission. These will include the parents keys to form a dot notation string
        description (str): An optional description of the permission.
        parent (Permission): The parent permission, if any.

    Methods:
        __repr__: Returns a string representation of the permission's ID with its parents keys in a dot notation.
        id: Returns the unique ID of the permission with its parents keys in a dot notation.

    """
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