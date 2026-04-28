from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings


async def _init_connection(conn):
    await conn.set_type_codec("geography", encoder=str, decoder=str, format="text", schema="public")
    await conn.set_type_codec("geometry", encoder=str, decoder=str, format="text", schema="public")


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
