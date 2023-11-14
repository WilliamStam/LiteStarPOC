from litestar import Controller, Request, Router, get

from guards.authorization import Authorize
from models.user import UserModel

class MyController(Controller):
    
    # the user must have this/these permissions to be able to access this route
    @get("/open")
    async def open(self, request: Request, user: UserModel) -> str:
        """totaly open route"""
        return f"all open | {user}"
    
    @get("/authenticated", guards=[Authorize()])
    async def authenticated(self, user: UserModel) -> str:
        """user must be authenticated"""
        return f"user must be authenticated | {user}"
    
    @get("/authorized1", guards=[Authorize(["perm1"])])
    async def authorized1(self, user: UserModel) -> str:
        """user must have ['perm1']"""
        return f"user must have ['perm1'] permission | {user}"
    
    @get("/authorized2", guards=[Authorize(["perm2", "perm3"])])
    async def authorized2(self, user: UserModel) -> str:
        """user must have ['perm2','perm3']"""
        return f"user must have ['perm2','perm3'] permission | {user}"


router = Router(
    "/segment1",
    route_handlers=[
        MyController,
    
    ],
)