import logging
from pathlib import Path

from litestar import Litestar
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.di import Provide
from litestar.logging import LoggingConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Components, SecurityScheme
from litestar.template import TemplateConfig

from router import router
from user import get_user, middleware_user_factory

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

app = Litestar(
    debug=True,
    route_handlers=[
        router
    ],
    openapi_config=OpenAPIConfig(
        title="my api",
        version="1.0.0",
        security=[{"BearerToken": []}],
        components=Components(
            security_schemes={
                "BearerToken": SecurityScheme(
                    type="http",
                    scheme="bearer",
                )
            },
        ),
    ),
    template_config=TemplateConfig(
        directory=Path("templates"),
        engine=JinjaTemplateEngine,
    ),
    dependencies={
        "user": Provide(get_user)
    },
    middleware=[
        middleware_user_factory
    ],
    logging_config=log_config
)