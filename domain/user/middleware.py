from litestar import Request
from litestar.types import ASGIApp, Receive, Scope, Send

from .model import UserModel


def UserMiddleware(app: ASGIApp) -> ASGIApp:
    async def user_middleware(scope: Scope, receive: Receive, send: Send) -> None:
        # Need to get the token to be able to go find the user
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
        
        # you would go find the user from the repo around here. im just taking a shortcut
        # you will now ALWAYS have a user model at request.user so you can safely use something like if request.user.is_authenticated() without first having to check if user is None
        # you can also probably generate a new key for the user if not logged in on redis or something and link "products" to that
        user = UserModel()
        if token:
            request.logger.info(f"Fetching user from database using token {token}")
            user = UserModel(
                id=1,
                name="im real",
                token=token,
                permissions=[
                    "perm1",
                    "perm2",
                    "perm4"
                ]
            )
        
        # attach the user to the request.user (available everywhere on request.user from here on out
        scope['user'] = user
        await app(scope, receive, send)
    
    return user_middleware