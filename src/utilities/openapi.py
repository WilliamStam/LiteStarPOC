from dataclasses import dataclass, field
from typing import Dict, List, Optional

from litestar.openapi.spec import Operation


@dataclass
class CustomOperation(Operation):
    x_scopes: Optional[List[str]] = field(default=None, metadata={"alias": "x-scopes"})
    x_requires_auth: Optional[bool] = field(default=False, metadata={"alias": "x-requires-authentication"})
    
    def __post_init__(self) -> None:
        self.x_scopes = []