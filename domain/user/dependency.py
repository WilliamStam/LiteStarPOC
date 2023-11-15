from typing import Annotated

from litestar import Request
from litestar.params import Dependency

from .model import UserModel


async def get_user(request: Request) -> UserModel:
    return request.user


User = Annotated[UserModel, Dependency()]