import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID"))  # your numeric Telegram user ID

# Handle files from admin only
async def forward_from_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        return  # Ignore all users except the admin

    file = update.message.document or update.message.video or update.message.audio or update.message.photo
    caption = update.message.caption or ""

    if file:
        if isinstance(file, list):  # for photos, pick the best quality
            file = file[-1]

        await context.bot.send_document(
            chat_id=CHANNEL_ID,
            document=file.file_id,
            caption=caption
        )
    else:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=caption)

# Main bot
def main() -> None:
    if not BOT_TOKEN or not CHANNEL_ID or not ADMIN_USER_ID:
        raise Exception("Missing environment variables")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Accept messages with files or media from admin only
    app.add_handler(MessageHandler(filters.ALL, forward_from_admin))

    app.run_polling()

if __name__ == "__main__":
    main()
