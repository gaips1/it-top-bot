from typing import Sequence
from sqlalchemy import Boolean, Column, Integer, String, select, BIGINT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import msgpack

from ..db import AsyncSessionLocal, Base, redis_client
from api.scraper import TopAcademyScraper
from api.models import *

evaluate_check_cooldown = {}

class User(Base):
    __tablename__ = 'users'

    id = Column(BIGINT, nullable=False, index=True, unique=True, primary_key=True, autoincrement=False)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    access_token = Column(String(255), nullable=True)

    @property
    def scraper(self):
        return TopAcademyScraper(self.id, self.username, self.password, self.access_token)
    
    async def get_user_info(self, id, state) -> StudentProfile | None:
        async with self.scraper as scraper:
            profile = await scraper.get_user_info()
            if not profile:
                from routers.auth import auth_handler
                await auth_handler(id, state, invalid=True)
                return None
            
        return profile
    
    async def get_leaderboard(self, id, state, is_group: bool = False):
        async with self.scraper as scraper:
            leaderboard = await scraper.get_leaderboard(is_group)
            if not leaderboard:
                from routers.auth import auth_handler
                await auth_handler(id, state, invalid=True)
                return None

        return leaderboard
        
    async def get_rewards(self, id, state):
        async with self.scraper as scraper:
            rewards = await scraper.get_rewards()
            if not rewards:
                from routers.auth import auth_handler
                await auth_handler(id, state, invalid=True)
                return None
            
        return rewards
        
    async def get_activities(self, state):
        async with self.scraper as scraper:
            activities = await scraper.get_activity()
            if not activities:
                from routers.auth import auth_handler
                await auth_handler(self.id, state, invalid=True)
                return None
            
        return activities.root
        
    async def get_homeworks(self, state, type: int, page: int = 1):
        async with self.scraper as scraper:
            homeworks = await scraper.get_homeworks(type, page)
            if not homeworks:
                from routers.auth import auth_handler
                await auth_handler(self.id, state, invalid=True)
                return None
            
        return homeworks.root
    
    async def get_homework_count(self, state):
        async with self.scraper as scraper:
            count = await scraper.get_homework_count()
            if not count:
                from routers.auth import auth_handler
                await auth_handler(self.id, state, invalid=True)
                return None
            
        return count.root
        
    async def get_lesson_evaluations(self, state):
        async with self.scraper as scraper:
            evaluations = await scraper.get_lesson_evaluations()
            if not evaluations:
                from routers.auth import auth_handler
                await auth_handler(self.id, state, invalid=True)
                return None
            
        return evaluations.root
        
    async def evaluate_lesson(
        self,
        key: str,
        mark_lesson: int,
        mark_teach: int,
        tags_lesson: list[str] = [],
        tags_teach: list[str] = []
    ) -> bool:
        async with self.scraper as scraper:
            success = await scraper.evaluate_lesson(
                {"key": key,
                "mark_lesson": mark_lesson,
                "mark_teach": mark_teach,
                "tags_lesson": tags_lesson,
                "tags_teach": tags_teach}
            )
        return success

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