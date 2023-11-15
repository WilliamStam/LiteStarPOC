# Litestar POC

Testing out a way to handle a user with permissions and the openapi docs only showing the accessible endpoints


## Routes 

setting up the routes with a `guards=[Authorize(...)]` kickstarts the process. (`api/segment1/routes.py`)

(the user: UserUodel dependency injection here is immaterial. ive just included it for viewing purposes. the user is found by the middleware instead)

```python
    @get("/open")
    async def open(self, request: Request, user: UserModel) -> str:
        """totaly open route"""
        return f"all open | {user}"
    
    @get("/authenticated", guards=[Authorize()])
    async def authenticated(self, user: UserModel) -> str:
        """user must be authenticated"""
        return f"user must be authenticated | {user}"
    
    @get("/authorized1", guards=[Authorize(["perm1"])])
    async def authorized1(self, user: UserModel) -> str:
        """user must have ['perm1']"""
        return f"user must have ['perm1'] permission | {user}"
    
    @get("/authorized2", guards=[Authorize(["perm2", "perm3"])])
    async def authorized2(self, user: UserModel) -> str:
        """user must have ['perm2','perm3']"""
        return f"user must have ['perm2','perm3'] permission | {user}"
```

the user middleware retrieves the current user and sets it to request.user.
 
the Authorize() guard checks that the supplied scopes and user correlates but it also houses a scopes property in it for later use since the guards object is available

since the Authorize guard has the desired scopes in it you can always loop through the guards to find an instance of Authorize and get the scopes from that guard (see part below). 

```python
    all_scopes = []
    for guard in handle.guards:
        #if the guard is a subclass of Authorize then we use its scopes
        # might be a good idea to lookup "all" authorize scopes and combine them incase somone goes wierd and guard=[Authorize("a"),Authorize("b")
        if isinstance(guard, Authorize):
            for scope in guard.scopes:
                all_scopes.append(scope)
    if all_scopes:
        request.logger.info(f"Scopes required for route {route.path} - {all_scopes}")

```

since this is a normal litestar guard it can be added to the Router() as well. (admin section and check if the user has "admin" permission anyone?)

```python
router = Router(
    "/segment2",
    route_handlers=[
        MyController,
    ],
    tags=[
        "checking permission on the Router as well"
    ],
    dependencies={"user": Provide(get_user)},
    guards=[Authorize(["seg2"])]
)
```

## OpenAPI spec

and this is where im stuck (`router.py`). i get the user object (thanks middleware). and the route scopes (thanks guards=Authorize) but not including the path is... 

```python
    @get("/openapi.json", include_in_schema=False)
    async def openapi(self, request: Request) -> ASGIResponse:
        request.logger.info(f"User: {request.user}")
        #2023-11-14 14:24:43,020 22268 INFO:root: User: id=1 name='im real' permissions=['perm1', 'perm2', 'perm4']
        
        for route in request.app.routes:
            for handle in route.route_handlers:
                if handle.guards is not None:
                    all_scopes = []
                    for guard in handle.guards:
                        #if the guard is a subclass of Authorize then we use its scopes
                        # might be a good idea to lookup "all" authorize scopes and combine them incase somone goes wierd and guard=[Authorize("a"),Authorize("b")
                        if isinstance(guard, Authorize):
                            for scope in guard.scopes:
                                all_scopes.append(scope)
                    if all_scopes:
                        request.logger.info(f"Scopes required for route {route.path} - {all_scopes}")
                        # 2023-11-14 14:22:43,646 14820 INFO:root: Scopes required for route /segment1/authenticated - []
                        # 2023-11-14 14:22:43,646 14820 INFO:root: Scopes required for route /segment1/authorized1 - ['perm1']
                        # 2023-11-14 14:22:43,646 14820 INFO:root: Scopes required for route /segment1/authorized2 - ['perm2', 'perm3']
                        
                        # DOESNT WORK :'(
                        handle.include_in_schema = False
        
        request.app._openapi_schema = None
        schema = request.app.openapi_schema.to_schema()
        json_encoded_schema = encode_json(schema, request.route_handler.default_serializer)
        return ASGIResponse(
            body=json_encoded_schema,
            media_type=OpenAPIMediaType.OPENAPI_JSON,
        )
```

## Authorize for openapi docs

Authorize() as a guard also sets up the security options on that path (so swagger gets the padlock icon for that route). this uses the
openapi_config.components.security_schemes defined

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
```

as soon as Authorize() is added as a guard it will automaticaly apply the security using those

```json
        "/segment1/authenticated": {
            "get": {
                // boring stuff
                },
                "deprecated": false,
                "security": [
                    {
                        "APIKeyQuery": []
                    },
                    {
                        "BearerToken": []
                    },
                    {
                        "APIKeyHeader": []
                    }
                ]
            }
        },
```

## User middleware

for the user middleware it will use the security setup as per above security_schemes to find the first "token" it finds

```python
def UserMiddleware(app: ASGIApp) -> ASGIApp:
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
        # do whatever you want with the token now
        print(token)
        
``` 

and this is just attached to the app like normal middleware

```python
app = Litestar(
    middleware=[
        UserMiddleware
    ],
)
```