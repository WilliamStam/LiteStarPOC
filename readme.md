# Litestar POC

Testing out a way to handle a user with permissions and the openapi docs only showing the accessible endpoints


## Routes 

setting up the routes with a `guards=[Authorize(...)]` kickstarts the process. (`api/segment1/routes.py`)

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