from litestar import Controller, Request, Router, get
from litestar.di import Provide

from domain.user.dependency import get_user, User
from domain.user.guard import Authorize
from utilities.openapi import CustomOperation
from utilities.permission import Permission

seg2 = Permission(
    key="seg2",
    description="User must have seg2"
)
perm1 = Permission(
    key="perm1",
    description="User must have seg2.perm1",
    parent=seg2
)
perm2 = Permission(
    key="perm2",
    description="User must have seg2.perm2",
    parent=seg2
)
perm3 = Permission(
    key="perm3",
    description="User must have seg2.perm3",
    parent=seg2
)

class MyController(Controller):
    
    # in all of thess routes im injecting the user object. this is NOT required for the auth system to work. its purely for my sanity checks
    
    # the user must have this/these permissions to be able to access this route
    @get("/open", description=f"User must have ['{seg2}'] permission since its attached to the router")
    async def open(self, request: Request, user: User,) -> str:
        """totaly open route"""
        return f"all open | {user}"
    
    @get("/authenticated", guards=[Authorize()], description=f"User must have ['{seg2}'] permission since its attached to the router")
    async def authenticated(self, user: User) -> str:
        return f"user must be authenticated and have '{seg2}' permission| {user}"
    
    @get("/authorized1", guards=[Authorize([perm1])],
        description=f"User must have ['{seg2}','{perm1}'] permissions"
    )
    async def authorized1(self, user: User) -> str:
        """user must have ['perm1']"""
        return f"user must have ['{seg2}','{perm1}'] permissions | {user}"
    
    @get("/authorized2", guards=[Authorize([perm2, perm3])],
        description=f"User must have ['{seg2}','{perm2}','{perm3}'] permissions")
    async def authorized2(self, user: User) -> str:
        """user must have ['perm2','perm3']"""
        return f"user must have ['{seg2}','{perm2}','{perm3}'] permission | {user}"

router = Router(
    "/segment2",
    route_handlers=[
        MyController,
    ],
    tags=[
        "seg2: checking permission on the Router and route"
    ],
    dependencies={"user": Provide(get_user)},
    guards=[Authorize(seg2)]
)