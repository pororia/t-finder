import logging
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

logger = logging.getLogger(__name__)


def _register_geography_codecs(dbapi_connection, connection_record):
    """asyncpg connection 이벤트에서 PostGIS geography/geometry 타입 코덱 등록."""
    asyncpg_conn = dbapi_connection.driver_connection
    for type_name in ("geography", "geometry"):
        try:
            dbapi_connection.await_(
                asyncpg_conn.set_type_codec(
                    type_name, encoder=str, decoder=str, format="text", schema="public"
                )
            )
        except Exception as e:
            logger.warning("PostGIS codec registration failed for %s: %s", type_name, e)


_connect_args: dict = {}
if settings.CLOUD_SQL_INSTANCE:
    # Cloud Run → Cloud SQL Unix 소켓 연결
    _connect_args["server_settings"] = {}
    _connect_args["host"] = f"/cloudsql/{settings.CLOUD_SQL_INSTANCE}"

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args=_connect_args,
)
event.listen(engine.sync_engine, "connect", _register_geography_codecs)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
