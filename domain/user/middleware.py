from litestar import Request
from litestar.types import ASGIApp, Receive, Scope, Send

from .model import UserModel


def middleware_user_factory(app: ASGIApp) -> ASGIApp:
    async def user_middleware(scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope)
        security_schemas = scope.get("app").openapi_config.components.security_schemes
        possible_tokens = []
        
        for key, schema in security_schemas.items():
            if schema.type == "apiKey" and schema.security_scheme_in=="query":
                possible_tokens.append(request.query_params.get(schema.name, None))
            elif schema.scheme == "bearer" and schema.type == "http":
                bearer_token = request.headers.get("Authorization", None)
                if bearer_token:
                    bearer_token = bearer_token.rsplit(' ', 1)[-1]
                possible_tokens.append(bearer_token)
            elif schema.type == "apiKey" and schema.security_scheme_in == "header":
                possible_tokens.append(request.headers.get(schema.name, None))
       
        token = next(
            (arg for arg in possible_tokens if arg is not None),
            None
        )
        
        
        
        scope['user'] = UserModel(
            id=1,
            name="im real",
            token=token,
            permissions=[
                "perm1",
                "perm2",
                "perm4"
            ]
        )
        await app(scope, receive, send)
    
    return user_middleware