import dataclasses
import logging
import mimetypes
import os
from pathlib import Path
from typing import Optional

from litestar import Controller, Request, Response, Router, get
from litestar.enums import MediaType, OpenAPIMediaType
from litestar.response import File, Template
from litestar.response.base import ASGIResponse
from litestar.serialization import encode_json

from api.segment1.router import router as segment1_router
from api.segment2.router import router as segment2_router

logger = logging.getLogger(__name__)

from domain.user.guard import Authorize


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
                if handle.guards is not None:
                    all_scopes = []
                    authed_route = False
                    for guard in handle.guards:
                        # if the guard is a subclass of Authorize then we use its scopes
                        # might be a good idea to lookup "all" authorize scopes and combine them incase somone goes wierd and guard=[Authorize("a"),Authorize("b")
                        if isinstance(guard, Authorize):
                            authed_route = True
                            for scope in guard.scopes:
                                all_scopes.append(scope)
                    if all_scopes:
                        request.logger.info(f"Scopes required for route {route.path} - {all_scopes}")
                        if not request.user.has_permissions(all_scopes):
                            pass
                            # handle.include_in_schema = False
                    if authed_route:
                        handle.security = secure_route_security
                    handle.operation_class.x_scopes = all_scopes
                    handle.operation_class.x_requires_auth = authed_route
                
        
        schema = request.app.openapi_schema.to_schema()
        # request.app.update_openapi_schema()
        # schema = request.app.openapi_config.to_openapi_schema()
        print(schema)
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


router = Router(
    "/",
    route_handlers=[
        OpenAPIController,
        StaticController,
        segment1_router,
        segment2_router,
        # system_router
    ]
)