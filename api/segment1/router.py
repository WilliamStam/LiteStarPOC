from litestar import Controller, Request, Router, get
from litestar.di import Provide

from domain.user.dependency import get_user, User
from domain.user.guard import Authorize
from utilities.permission import Permission


perm1 = Permission(
    key="perm1",
    description="User must have perm1",
)
perm2 = Permission(
    key="perm2",
    description="User must have perm2",
)
perm3 = Permission(
    key="perm3",
    description="User must have perm3",
)
class MyController(Controller):
    
    # in all of thess routes im injecting the user object. this is NOT required for the auth system to work. its purely for my sanity checks
    
    # the user must have this/these permissions to be able to access this route
    @get("/open", description="No user required. no padlock")
    async def open(self, user: User) -> str:
        return f"all open | {user} | \n user is empty cause we arent requiring them to be logged in and the docs arent passing in the key.\n force security on all paths to prohibit this"
    
    @get("/authenticated", guards=[Authorize()], description="The user must be logged in. shows padlock")
    async def authenticated(self, user: User) -> str:
        return f"user must be authenticated | {user}"
    
    @get("/authorized1", guards=[Authorize([perm1])], description=f"The user must be logged in and have ['{perm1}'] permission. shows padlock")
    async def authorized1(self, user: User) -> str:
        return f"user must have ['{perm1}'] permission | {user}"
    
    @get("/authorized2", guards=[Authorize([perm2, perm3])],
        description=f"The user must be logged in and have ['{perm2}','{perm3}'] permissions. shows padlock - \n(our user is missing {perm3} here hence forbidden)")
    async def authorized2(self, user: User) -> str:
        return f"user must have ['{perm2}','{perm3}'] permission | {user}"


router = Router(
    "/segment1",
    route_handlers=[
        MyController,
    ],
    tags=[
        "seg1: only checking permissions on the route"
    ],
    dependencies={"user": Provide(get_user)}
)