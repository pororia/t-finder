import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

logger = logging.getLogger(__name__)


async def _init_connection(conn):
    for type_name in ("geography", "geometry"):
        try:
            await conn.set_type_codec(
                type_name, encoder=str, decoder=str, format="text", schema="public"
            )
            logger.debug("Registered asyncpg codec for %s", type_name)
        except Exception as e:
            logger.error("Failed to register asyncpg codec for %s: %r", type_name, e)


_connect_args: dict = {"init": _init_connection}
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
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
