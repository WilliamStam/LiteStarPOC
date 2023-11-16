the user middleware retrieves the current user and sets it to request.user.

and this is just attached to the app like normal middleware

```python
from domain.user.middleware import UserMiddleware
app = Litestar(
    # ...
    middleware=[
        UserMiddleware
    ],
    # ...
)
```

The user middleware will go through the security schemas setup for openapi and use those to try find the token to use to lookup the user

penapi_config.components.security_schemes defined

```python
app = Litestar(
    # ...
    openapi_config=OpenAPIConfig(
        # ...
        security=[], # setting this to a blank list removes the padlock from every "other" page. so padlock becomes opt in
        components=Components(
            security_schemes={ # do what you please here with the security setups
                "APIKeyQuery": SecurityScheme(
                    type="apiKey",
                    description="Pass the token via a query sting item ?token=xxx",
                    security_scheme_in="query",
                    name="token",
                ),
                "BearerToken": SecurityScheme(
                    type="http",
                    scheme="bearer",
                    description="Use a bearer token for authorization"
                ),
                "APIKeyHeader": SecurityScheme(
                    type="apiKey",
                    description="Add a header [X-API-Key] with the token",
                    security_scheme_in="header",
                    name="X-API-Key",
                )
            },
        ),
    ),
    #...
)
```

the user model will now be available anywhere where you can get the "request" object from the system

```python
@get("/")
async def home(request: Request) -> UserModel:
    return request.user

```