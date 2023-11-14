import logging
from pathlib import Path

from litestar import Litestar, Request
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.logging import LoggingConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Components, SecurityScheme
from litestar.template import TemplateConfig

from middleware.user import middleware_user_factory
from router import router

log_config = LoggingConfig(
    root={
        "level": logging.getLevelName(logging.INFO),
        "handlers": [
            "console"
        ]
    },
    formatters={
        "standard": {
            "format": "%(asctime)s %(process)s %(levelname)s:%(name)s: %(message)s"
        }
    },
)

logger = log_config.configure()()

from models.user import UserModel





app = Litestar(
    debug=True,
    route_handlers=[
        router
    ],
    openapi_config=OpenAPIConfig(
        title="my api",
        version="1.0.0",
        security=[],
        components=Components(
            security_schemes={
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
    template_config=TemplateConfig(
        directory=Path("templates"),
        engine=JinjaTemplateEngine,
    ),
    
    middleware=[
        middleware_user_factory
    ],
    
    logging_config=log_config
)