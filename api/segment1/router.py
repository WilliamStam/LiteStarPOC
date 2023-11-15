from litestar import Controller, Request, Router, get
from litestar.di import Provide

from domain.user.dependency import get_user, User
from domain.user.guard import Authorize
from utilities.openapi import CustomOperation
class MyController(Controller):
    
    # the user must have this/these permissions to be able to access this route
    @get("/open")
    async def open(self, request: Request, user: User) -> str:
        """totaly open route"""
        return f"all open | {user}"
    
    @get("/authenticated", guards=[Authorize()], operation_class=CustomOperation)
    async def authenticated(self, user: User) -> str:
        """user must be authenticated"""
        return f"user must be authenticated | {user}"
    
    @get("/authorized1", guards=[Authorize(["perm1"])])
    async def authorized1(self, user: User) -> str:
        """user must have ['perm1']"""
        return f"user must have ['perm1'] permission | {user}"
    
    @get("/authorized2", guards=[Authorize(["perm2", "perm3"])])
    async def authorized2(self, user: User) -> str:
        """user must have ['perm2','perm3']"""
        return f"user must have ['perm2','perm3'] permission | {user}"


router = Router(
    "/segment1",
    route_handlers=[
        MyController,
    
    ],
    dependencies={"user": Provide(get_user)}
)