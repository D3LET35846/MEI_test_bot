# database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime

from config import DATABASE_URL

# Create base class for database models
Base = declarative_base()

# Create async engine for database connection
engine = create_async_engine(DATABASE_URL)

# Create session factory to create sessions
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Function to initialize the database
async def init_db():
    # Create all tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Define User model for storing user data
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    is_subscribed = Column(Boolean, default=False)
    name = Column(String, nullable=True)
    group = Column(String, nullable=True)
    send_date = Column(DateTime, nullable=True)
    send_after = Column(Integer, nullable=True)
    letter_filename = Column(String, nullable=True)