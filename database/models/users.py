from typing import Sequence
from sqlalchemy import Boolean, Column, Integer, String, select, BIGINT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import msgpack

from ..db import AsyncSessionLocal, Base, redis_client
from api.scraper import TopAcademyScraper
from api.models.userinfo import StudentProfile

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'ittopbot'}

    id = Column(BIGINT, nullable=False, index=True, unique=True, primary_key=True, autoincrement=False)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    access_token = Column(String, nullable=True)

    @property
    def scraper(self):
        return TopAcademyScraper(self.username, self.password, self.access_token)
    
    async def get_user_info(self, id, state) -> StudentProfile | None:
        async with self.scraper as scraper:
            profile = await scraper.get_user_info()
            if not profile:
                from routers.auth import auth_handler
                await auth_handler(id, state, invalid=True)
                return None
            
            await self.update(access_token=scraper.access_token)
            
            return profile
    
    async def get_leaderboard(self, id, state, is_group: bool = False):
        async with self.scraper as scraper:
            leaderboard = await scraper.get_leaderboard(is_group)
            if not leaderboard:
                from routers.auth import auth_handler
                await auth_handler(id, state, invalid=True)
                return None
            
            await self.update(access_token=scraper.access_token)

            return leaderboard
        
    async def get_rewards(self, id, state):
        async with self.scraper as scraper:
            rewards = await scraper.get_rewards()
            if not rewards:
                from routers.auth import auth_handler
                await auth_handler(id, state, invalid=True)
                return None
            
            await self.update(access_token=scraper.access_token)
            
            return rewards

    async def update(self, **kwargs):
        session: AsyncSession
        async with AsyncSessionLocal() as session:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            try:
                await session.merge(self)
                await session.commit()
                data = {"id": self.id, "username": self.username, "password": self.password, "access_token": self.access_token}
                await redis_client.set(f"user:{self.id}", msgpack.dumps(data))
                return self
            except SQLAlchemyError as e:
                print(f"Error updating user: {e}")
                await session.rollback()

async def get_users() -> Sequence[User]:
    session: AsyncSession
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users
    
async def create_user(**kwargs):
    session: AsyncSession
    async with AsyncSessionLocal() as session:
        user = User(**kwargs)
        try:
            session.add(user)
            await session.commit()
            await redis_client.set(f"user:{user.id}", msgpack.dumps({**kwargs}))
            return user
        
        except IntegrityError:
            await session.rollback()
            usr = await get_user_by_id(kwargs.get('id'))
            await usr.update(**kwargs)
            return usr
        
        except Exception as e:
            print(f"Error creating user: {e}")
            await session.rollback()
            return None
    
async def get_user_by_id(id: int) -> User | None:
    cached_user = await redis_client.get(f"user:{id}")
    if cached_user:
        data = msgpack.loads(cached_user)
        return User(**data)

    session: AsyncSession
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalars().first()
        if user:
            data = {"id": user.id,"username": user.username,"password": user.password,"access_token": user.access_token}
            await redis_client.set(f"user:{id}", msgpack.dumps(data))
        return user
    
async def delete_user(id: int) -> bool:
    session: AsyncSession
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(User).where(User.id == id))
            user = result.scalars().first()
            if user:
                await session.delete(user)
                await session.commit()
                await redis_client.delete(f"user:{id}")
                return True
            return False
        except SQLAlchemyError as e:
            print(f"Error deleting user: {e}")
            await session.rollback()
            return False