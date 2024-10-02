from .models import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import asyncpg


# To use local postgres database uncommit this on:
# DATABASE_URL = "postgresql+asyncpg://postgres:12345@localhost:5432/sops_db"

# To use postgres container of docker uncommit this on:
DATABASE_URL = "postgresql+asyncpg://postgres:12345@db:5432/sops_db"


# SQLAlchemy 2.0 is used
engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_database_if_not_exists():
    user = "postgres"
    password = "12345"
    # host = "localhost"   # Local host
    host = "db"        # Docker container host
    db_name = "sops_db"

    conn = await asyncpg.connect(user=user, password=password, host=host, database="postgres")

    result = await conn.fetchval(f"SELECT 1 FROM pg_database WHERE datname='{db_name}';")

    if not result:
        await conn.execute(f'CREATE DATABASE "{db_name}";')

    await conn.close()


async def init_db():
    await create_database_if_not_exists()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
