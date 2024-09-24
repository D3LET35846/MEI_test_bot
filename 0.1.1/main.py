# main.py
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import API_TOKEN
from handlers import router
from database import init_db

# Basic logging configuration
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

# Main function to start the bot
async def main():
    # Initialize/create database tables
    await init_db()
    # Start polling for updates
    await dp.start_polling(bot)

# Run the bot if the script is executed directly
if __name__ == '__main__':
    asyncio.run(main())