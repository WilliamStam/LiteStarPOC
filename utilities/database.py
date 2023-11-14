import dataclasses
from typing import Optional

from sqlalchemy import Engine, URL, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from log import log

logger = log.getLogger(__name__)


@dataclasses.dataclass
class DatabaseConfig():
    drivername: str
    username: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    schema: Optional[str] = None


class TableBase(DeclarativeBase):
    pass


class DatabaseEngineMissing(Exception):
    """A database engine hasn't been added"""


class Database():
    
    def __init__(self, engine: Engine = None, schema=None, **kwargs):
        self.db = None
        self.engine = engine
        self.schema = schema
        self.declarative_base = declarative_base()
        self.kwargs = kwargs
        
        self.set_engine(engine=engine, schema=schema, **kwargs)
    
    def set_engine(self, engine: Engine = None, schema=None, **kwargs):
        self.engine = engine
        self.db = sessionmaker(bind=self.engine, **kwargs)
        self.schema = schema
    
    async def __aenter__(self):
        if self.db is None:
            raise DatabaseEngineMissing()
        
        self.session: Session = self.db()
        self.label = self.session.bind.engine.url
        logger.debug(f"Creating database session: {self.label}")
        
        # cant set the schema on oracle in the connection
        if self.schema:
            self.session.execute(text(f"ALTER SESSION SET CURRENT_SCHEMA = {self.schema}"))
        
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.debug(f"Closing database session: {self.label}")
        self.session.close()


def create_connection(db: DatabaseConfig, **kwargs) -> Database:
    engine = create_engine(
        URL.create(
            drivername=db.drivername or None,
            username=db.username or None,
            password=db.password or None,
            host=db.host or None,
            port=db.port or None,
            database=db.database or None,
        )
    )
    k = kwargs
    k['schema'] = db.schema
    
    return Database(engine=engine, **k)