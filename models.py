import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func


load_dotenv()
PG_DSN = f"postgresql+asyncpg://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@127.0.0.1:5431/{os.getenv('PG_DB')}"
engine = create_async_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Ad(Base):
    __tablename__ = 'ads'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=True, unique=True, index=True)
    description = Column(String, nullable=True)
    creation_time = Column(DateTime, server_default=func.now())
    owner = Column(String, nullable=True)
