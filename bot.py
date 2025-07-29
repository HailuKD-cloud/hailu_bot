import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
OWNER_ID = int(os.getenv("OWNER_ID"))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to track categories and files
file_groups = {}

async def start(update: Update, context: CallbackContext):
    args = context.args
    if args:
        group = args[0].lower()
        files = file_groups.get(group)
        if files:
            await update.message.reply_text(f"📂 Files in '{group}':")
            for file_id, caption in files:
                await update.message.reply_document(file_id, caption=caption)
        else:
            await update.message.reply_text("❌ No files found for that category.")
    else:
        await update.message.reply_text("Welcome! Send a group name (like 'season1') and upload your files.")

async def setgroup(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("⛔ You're not allowed to set categories.")
    
    if context.args:
        context.user_data['current_group'] = context.args[0].lower()
        await update.message.reply_text(f"✅ Group set to '{context.args[0]}'. Now upload files.")
    else:
        await update.message.reply_text("❗ Usage: /setgroup group_name")

async def handle_file(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("⛔ Only the admin can upload files.")
    
    group = context.user_data.get('current_group')
    if not group:
        return await update.message.reply_text("❗ Use /setgroup before uploading files.")

    doc = update.message.document or update.message.video or update.message.audio
    if not doc:
        return await update.message.reply_text("❗ Only documents, videos, or audio files allowed.")

    # Forward to storage channel
    sent = await context.bot.send_document(
        chat_id=CHANNEL_ID,
        document=doc.file_id,
        caption=update.message.caption or ""
    )

    file_id = sent.document.file_id
    file_groups.setdefault(group, []).append((file_id, update.message.caption or "No caption"))

    await update.message.reply_text("✅ File saved and added to group!")

async def unknown(update: Update, context: CallbackContext):
    await update.message.reply_text("❓ Unknown command.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setgroup", setgroup))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL | filters.Audio.ALL, handle_file))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    logger.info("Bot running...")
    app.run_polling()

if __name__ == '__main__':
    main()
