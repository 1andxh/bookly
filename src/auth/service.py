from .models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from .schemas import UserCreateModel
from .utils import hash_password


class UserAuthService():
    async def get_user_by_email(self, email:str, session: AsyncSession ):
        statement  = select(User).where(User.email == email)

        result  = await session.exec(statement)
        user = result.first()
        return user
    
    async def check_user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        if user is None:
           return False
        return True
    
    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()

        new_user = User(
            **user_data_dict
        )
        new_user.password_hash = hash_password(user_data_dict['password'])
        new_user.role = 'User'

        session.add(new_user)

        await session.commit()

        return new_user