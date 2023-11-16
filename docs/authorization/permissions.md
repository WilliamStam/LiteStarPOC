

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