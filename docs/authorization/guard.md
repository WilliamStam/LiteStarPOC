The user model has a parameter "permissions" which should be stored in the database as a json list. and should look like this

```python
permissions: list[str] = [
    "permission1",
    "parent.child.sub"
]
```


setting up a routes with a `guards=[Authorize(...)]` kickstarts the process.


```python
@get("/open")
async def open(self) -> str:
    """totaly open route"""
    return f"all open"

@get("/authenticated", guards=[Authorize()])
async def authenticated(self) -> str:
    """user must be authenticated"""
    return f"user must be authenticated"

@get("/authorized1", guards=[Authorize(["perm1"])])
async def authorized1(self) -> str:
    """user must have ['perm1']"""
    return f"user must have ['perm1'] permission"

@get("/authorized2", guards=[Authorize(["perm2", "perm3"])])
async def authorized2(self) -> str:
    """user must have ['perm2','perm3']"""
    return f"user must have ['perm2','perm3'] permission"
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


## Authorize for openapi docs

Authorize() as a guard also sets up the security options on that path (so swagger gets the padlock icon for that route). this uses the
openapi_config.components.security_schemes defined (see user)

as soon as Authorize() is added as a guard it will automaticaly apply the security using those to the openapi doc spec to force a padlock icon in the ui

```json
"/segment1/authenticated": {
    "get": {
        // boring stuff
        },
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


# Permission objects

you'll notice in the above im using a string for the various permissions, this was done for readability. in the code i make use of a permission object instead

```python
from ustilities.permission import Permission
parent = Permission(
    key="parent",
    description="User must have parent"
)
child = Permission(
    key="child",
    description="User must have parent.child",
    parent=parent
)
grandchild = Permission(
    key="perm1",
    description="User must have parent.child.grandchild",
    parent=child
)

```
the permissin object can be layered all you want infinitely. 
the grandchild.id (or str(grandchild)) will build a dot notated sting of all the parents so in this case "parent.child.grandchild"

## a list of permissions

i also have a permissions.py file in the root with the permission collection. 

```python
from utilities.permission import PermissionCollection
system_permissions = PermissionCollection()
```

Authorize() adds all permissions (whether its on Router() or the route) to this collection. 

with a simpleish route like 

```python
# im using pydantic models
class PermissionItem(BaseModel):
    key: Optional[str] = None
    description: Optional[str] = None
    parent: Optional[str] = None

class PermissionsResponse(BaseModel):
    system: List[PermissionItem] = Field(default_factory=list)
    
@get("/permissions",description="Get all the system permissions")
async def get_all_permissions_used() -> PermissionsResponse:
    from permissions import system_permissions
    
    response = PermissionsResponse()
    for row in system_permissions:
        response.system.append(
            PermissionItem(
                key=row.id,
                description=row.description,
                parent=str(row.parent) if row.parent else None,
            )
        )
        
    return response
```

you now end up with a list of permissions used in the system (incase you want to build a checkbox tree thing for allowing the user permissions or for documentation)

<sub>(this has gone back to using the routes permissions in the api part instead of the parent, child, grandchild example above)</sub>
```json
{
  "system": [
    {
      "key": "perm1",
      "description": "User must have perm1",
      "parent": null
    },
    {
      "key": "perm2",
      "description": "User must have perm2",
      "parent": null
    },
    {
      "key": "perm3",
      "description": "User must have perm3",
      "parent": null
    },
    {
      "key": "seg2.perm1",
      "description": "User must have seg2.perm1",
      "parent": "seg2"
    },
    {
      "key": "seg2.perm2",
      "description": "User must have seg2.perm2",
      "parent": "seg2"
    },
    {
      "key": "seg2.perm3",
      "description": "User must have seg2.perm3",
      "parent": "seg2"
    },
    {
      "key": "seg2",
      "description": "User must have seg2",
      "parent": null
    }
  ]
}

```