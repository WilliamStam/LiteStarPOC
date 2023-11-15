from typing import List, Optional

from litestar.connection import ASGIConnection
from litestar.handlers import BaseRouteHandler

from litestar.exceptions import NotAuthorizedException, PermissionDeniedException


# @get("/authenticated", guards=[Authorize()]) - user must be authenticated to see this route
# @get("/authorized2", guards=[Authorize(["perm2", "perm3"])]) - user must have all of those permissions to see this route

# you could also probably accept False in scopes and then make sure the user ISNT logged in. it would just be a union in the init and a check if self.scopes == False and if user.is_authed() then raise error
class Authorize():
    
    def __init__(self, scopes: Optional[List[str]] = None):
        if scopes is None:
            scopes = []
        self.scopes = scopes
    
    async def __call__(self, connection: ASGIConnection, route_handler: BaseRouteHandler):
        connection.logger.info(f"user: {connection.user}")
        if connection.user.id is None:
            connection.logger.warning("user isn't authenticated")
            raise NotAuthorizedException()
        
        missing_scopes = []
        for scope in self.scopes:
            if str(scope) not in connection.user.permissions:
                missing_scopes.append(str(scope))
        
        if missing_scopes:
            connection.logger.warning(f"User missing scope '{missing_scopes}'")
            raise PermissionDeniedException()