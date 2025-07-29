import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID"))  # Set this in Railway
PUBLIC_CHANNEL_ID = os.getenv("PUBLIC_CHANNEL_ID")  # e.g., "@publicchannel"
PRIVATE_CHANNEL_ID = os.getenv("PRIVATE_CHANNEL_ID")  # e.g., "@privatechannel"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Start command - for you only
@dp.message_handler(Command("start"))
async def start_command(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        await message.reply("Welcome, Admin! Send me your post details.")
    else:
        await message.reply("Hi! Please check out our public channel for updates.")

# Handle posts from you (admin)
@dp.message_handler(lambda message: message.from_user.id == ADMIN_USER_ID, content_types=types.ContentTypes.TEXT | types.ContentTypes.PHOTO)
async def handle_admin_post(message: types.Message):
    if message.caption:
        caption = message.caption
    else:
        caption = message.text

    # Add "View & Download" button that links to your private channel
    buttons = InlineKeyboardMarkup().add(
        InlineKeyboardButton("📥 View & Download", url=f"https://t.me/{PRIVATE_CHANNEL_ID.lstrip('@')}")
    )

    if message.photo:
        await bot.send_photo(chat_id=PUBLIC_CHANNEL_ID, photo=message.photo[-1].file_id, caption=caption, reply_markup=buttons)
    else:
        await bot.send_message(chat_id=PUBLIC_CHANNEL_ID, text=caption, reply_markup=buttons)

    await message.reply("✅ Posted to public channel with download link.")

# Fallback for others trying to interact
@dp.message_handler()
async def fallback_handler(message: types.Message):
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply("Access denied. Visit our public channel for latest files!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
