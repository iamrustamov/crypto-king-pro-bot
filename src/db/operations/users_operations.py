from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserModel


async def get_user(
    user_id: int,
    db_session: AsyncSession,
) -> UserModel | None:
    async with db_session as session:
        return await session.get(UserModel, user_id)


async def get_or_create_user(
    user_id: int,
    username: str | None,
    db_session: AsyncSession,
) -> UserModel:
    user_obj: UserModel | None = await get_user(user_id, db_session)
    if not user_obj:
        async with db_session as session:
            async with session.begin():
                user_obj: UserModel = UserModel(
                    user_id=user_id,
                    username=username,
                )
                session.add(user_obj)
            await session.refresh(user_obj)
    return user_obj
