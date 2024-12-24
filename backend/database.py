from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker


USER = "postgres.butirdbrcndkntvqcssi"
PASSWORD = "8ylqOJlqvN8yIvH0"
HOST = "aws-0-eu-central-1.pooler.supabase.com"
PORT = "5432"
DBNAME = "postgres"

url = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"

Base = declarative_base()

engine = create_async_engine(url, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        # await conn.run_sync(Base.metadata.create_all)
        pass
