from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import delete, select

from models import User

async def get_user_by_query(session: AsyncSession, where):
    query = select(User).where(where)
    user = (await session.execute(query)).scalar_one_or_none()

    return user