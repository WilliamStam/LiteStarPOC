from typing import List, Union

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException, PermissionDeniedException
from litestar.handlers import BaseRouteHandler

from utilities.permission import Permission
from permissions import system_permissions
from utilities.openapi import CustomOperation


# @get("/authenticated", guards=[Authorize()]) - user must be authenticated to see this route
# @get("/authorized2", guards=[Authorize(["perm2", "perm3"])]) - user must have all of those permissions to see this route

# you could also probably accept False in scopes and then make sure the user ISNT logged in. it would just be a union in the init and a check if self.scopes == False and if user.is_authed() then raise error
class Authorize():
    
    def __init__(
        self,
        permissions: Union[
            Permission,
            List[Permission],
            None
        ] = None
    ):
        if permissions is None:
            permissions = []
        
        if isinstance(permissions, Permission):
            permissions = [permissions]
            
        for perm in permissions:
            system_permissions.add(perm)
        
        self.permissions = permissions
    
    async def __call__(self, connection: ASGIConnection, route_handler: BaseRouteHandler):
        connection.logger.info(f"user: {connection.user}")
        if connection.user.id is None:
            connection.logger.warning("user isn't authenticated")
            raise NotAuthorizedException()
        
        missing_permissions = []
        for permission in self.permissions:
            if str(permission) not in connection.user.permissions:
                missing_permissions.append(str(permission))
        
        if missing_permissions:
            connection.logger.warning(f"User missing permission(s) {missing_permissions}")
            raise PermissionDeniedException()