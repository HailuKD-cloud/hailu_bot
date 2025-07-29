import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID"))  # Your Telegram ID
PUBLIC_CHANNEL_ID = os.getenv("PUBLIC_CHANNEL_ID")  # e.g., "@movies_free04"
PRIVATE_CHANNEL_ID = os.getenv("PRIVATE_CHANNEL_ID")  # e.g., "@hfiles04"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Start command
@dp.message_handler(Command("start"))
async def start_command(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        await message.reply("Welcome, Admin! Send me your post.")
    else:
        await message.reply("Hi! Please visit our public channel for updates.")

# Handle admin post
@dp.message_handler(lambda message: message.from_user.id == ADMIN_USER_ID, content_types=types.ContentTypes.ANY)
async def handle_admin_post(message: types.Message):
    caption = message.caption or message.text or "New content available!"

    # First, post full content to PRIVATE channel
    if message.photo:
        await bot.send_photo(chat_id=PRIVATE_CHANNEL_ID, photo=message.photo[-1].file_id, caption=caption)
    elif message.video:
        await bot.send_video(chat_id=PRIVATE_CHANNEL_ID, video=message.video.file_id, caption=caption)
    elif message.document:
        await bot.send_document(chat_id=PRIVATE_CHANNEL_ID, document=message.document.file_id, caption=caption)
    else:
        await bot.send_message(chat_id=PRIVATE_CHANNEL_ID, text=caption)

    # Then, post preview + button to PUBLIC channel
    download_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("📥 View & Download", url=f"https://t.me/{PRIVATE_CHANNEL_ID.lstrip('@')}")
    )

    if message.photo:
        await bot.send_photo(chat_id=PUBLIC_CHANNEL_ID, photo=message.photo[-1].file_id, caption=caption, reply_markup=download_button)
    else:
        await bot.send_message(chat_id=PUBLIC_CHANNEL_ID, text=caption, reply_markup=download_button)

    await message.reply("✅ Posted to private & public channels as intended.")

# Fallback for non-admin users
@dp.message_handler()
async def fallback_handler(message: types.Message):
    if message.from_user.id != ADMIN_USER_ID:
        await message.reply("Access denied. Visit our public channel for updates!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
