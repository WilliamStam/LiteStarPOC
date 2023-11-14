from typing import Optional, List

from litestar import Request
from litestar.types import ASGIApp, Receive, Scope, Send
from pydantic import BaseModel, Field

class UserModel(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    
async def get_user(request:Request) -> UserModel:
    return request.user
    


def middleware_user_factory(app: ASGIApp) -> ASGIApp:
    async def user_middleware(scope: Scope, receive: Receive, send: Send) -> None:
        scope['user'] = UserModel(
            id=1,
            name="im real",
            permissions=[
                "perm1",
                "perm2",
                "perm4"
            ]
        )
        await app(scope, receive, send)
    
    return user_middleware