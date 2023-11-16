import dataclasses
import logging
import mimetypes
import os
from pathlib import Path
from typing import Dict, List, Optional

from litestar import Controller, Request, Response, Router, get
from litestar.enums import MediaType, OpenAPIMediaType
from litestar.response import File, Template
from litestar.response.base import ASGIResponse
from litestar.serialization import encode_json
from pydantic import BaseModel, Field

from api.segment1.router import router as segment1_router
from api.segment2.router import router as segment2_router

logger = logging.getLogger(__name__)

from domain.user.guard import Authorize
from utilities.openapi import CustomOperation

class OpenAPIController(Controller):
    
    # i pass a few extra things into the template like company logo etc
    # so rather use my "own" template for the docs
    @get("/", include_in_schema=False)
    async def docs(self, request: Request) -> Template:
        return Template(template_name="rapidoc.jinja", context={"app": request.app}, media_type=MediaType.HTML)
    
    @get("/favicon.ico", include_in_schema=False)
    async def favicon(self) -> File:
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(dir_path, 'static', 'icon.ico')
        return File(
            path=path,
            filename="favicon.ico",
            content_disposition_type="attachment",
        )
    
    # all good apis have a openapi.json file right...
    @get("/openapi.json", include_in_schema=False)
    async def openapi(self, request: Request) -> ASGIResponse:
        request.logger.info(f"User: {request.user}")
        
        schemas = []
        for key, value in request.app.openapi_config.components.security_schemes.items():
            schemas.append({key: []})
        secure_route_security = schemas
        
        for route in request.app.routes:
            for handle in route.route_handlers:
                handle.operation_class = CustomOperation
        
                all_permission = []
                authed_route = False
                if handle.guards is not None:
                    for guard in handle.guards:
                        # if the guard is a subclass of Authorize then we use its scopes
                        # might be a good idea to lookup "all" authorize scopes and combine them incase somone goes wierd and guard=[Authorize("a"),Authorize("b")
                        if isinstance(guard, Authorize):
                            authed_route = True
                            for permission in guard.permissions:
                                all_permission.append(str(permission))
                    if all_permission:
                        request.logger.info(f"Scopes required for route {route.path} - {all_permission}")
                        
                    if authed_route:
                        handle.security = secure_route_security
                        if not request.user.has_permissions(all_permission):
                            pass
                            # handle.include_in_schema = False
                    handle.opt["x-scopes"] = all_permission
                    handle.opt["x-requires-authentication"] = True
                    
                    pass
                
                # handle.operation_id.description = "woof"
                    # handle.operation_class.x_scopes = all_permission
                    # handle.operation_class.x_requires_auth = authed_route
            pass
        raw_schema = request.app.openapi_schema
        schema = request.app.openapi_schema.to_schema()
        json_encoded_schema = encode_json(schema, request.route_handler.default_serializer)
        return ASGIResponse(
            body=json_encoded_schema,
            media_type=OpenAPIMediaType.OPENAPI_JSON,
        )


# i pass all my static files through a function to make sure the types are allowed etc.
# especially useful for images where you can set the width / height / resize / whatever based on query params
class StaticController(Controller):
    
    @get("/static/{rest_of_path:path}", include_in_schema=False)
    async def static(
        self,
        request: Request,
        rest_of_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        resize: Optional[bool] = None,
    ) -> Response:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        mimetype, encoding = mimetypes.guess_type(rest_of_path)
        
        full_path = Path(f"{dir_path}/static/{rest_of_path}")
        logger.info(dir_path)
        
        basename = os.path.basename(full_path)
        return File(
            path=full_path,
            media_type=mimetype,
            content_disposition_type="inline",
            filename=basename
        )


# ----------------------
# BONUS since we're using objects for permissions everhwre now and the Autho() adds each to the system permissions we can get a list of all permissions used in the system

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


router = Router(
    "/",
    route_handlers=[
        OpenAPIController,
        StaticController,
        segment1_router,
        segment2_router,
        get_all_permissions_used
    ]
)