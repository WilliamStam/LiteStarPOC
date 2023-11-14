from litestar.types import ASGIApp, Receive, Scope, Send

from models.user import UserModel


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