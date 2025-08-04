import logging
import os
from datetime import timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment configs
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_DOC_ID = os.getenv("GOOGLE_DOC_ID")

# Google Service Account Credentials (still embedded, replace for prod)
SERVICE_ACCOUNT_CREDS = {
    "type": "service_account",
    "project_id": "reminder02",
    "private_key_id": "4c1d4ae61d8687084fff41d6227a7cad6e4c6eb2",
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('GOOGLE_CLIENT_EMAIL').replace('@', '%40')}",
    "universe_domain": "googleapis.com"
}

# Store active user jobs
user_jobs = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton("10 min ⏰", callback_data="10"),
            InlineKeyboardButton("30 min ⏰", callback_data="30"),
            InlineKeyboardButton("1 hour ⏰", callback_data="60"),
        ],
        [InlineKeyboardButton("Stop Reminders ❌", callback_data="stop")],
    ]

    doc_content = await get_google_doc_content()
    welcome_msg = (
        f"👋 Hello {user.mention_html()}! Welcome to *iFart Token Mini App* Reminder Bot!\n\n"
        f"{doc_content}\n\n🚀 Set your reminder interval:"
    )

    await update.message.reply_html(welcome_msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def get_google_doc_content() -> str:
    try:
        creds = service_account.Credentials.from_service_account_info(
            SERVICE_ACCOUNT_CREDS, scopes=["https://www.googleapis.com/auth/documents.readonly"]
        )
        service = build("docs", "v1", credentials=creds)
        doc = service.documents().get(documentId=GOOGLE_DOC_ID).execute()

        content = []
        for element in doc.get("body", {}).get("content", []):
            if "paragraph" in element:
                for para in element["paragraph"]["elements"]:
                    if "textRun" in para:
                        content.append(para["textRun"]["content"])

        return "".join(content).strip() or "⚠️ Whale 🐳 alert! Buy before presale ends!"
    except Exception as e:
        logger.error(f"Google Doc error: {e}")
        return "⚠️ Whale 🐳 alert! Buy before presale ends!"

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if query.data == "stop":
        if user_id in user_jobs:
            for job in user_jobs[user_id]:
                job.schedule_removal()
            del user_jobs[user_id]
            await query.edit_message_text("✅ Reminders stopped. Use /start to begin again.")
        else:
            await query.edit_message_text("ℹ️ No active reminders to stop.")
        return

    try:
        minutes = int(query.data)
    except ValueError:
        logger.error(f"Invalid callback: {query.data}")
        return

    # Remove old jobs
    if user_id in user_jobs:
        for job in user_jobs[user_id]:
            job.schedule_removal()

    job = context.job_queue.run_repeating(
        callback=send_reminder,
        interval=timedelta(minutes=minutes),
        first=0,
        chat_id=chat_id,
        data={"user_id": user_id, "minutes": minutes},
        name=str(user_id),
    )

    user_jobs[user_id] = [job]

    intervals = {10: "10 minutes", 30: "30 minutes", 60: "1 hour"}
    await query.edit_message_text(
        f"🔔 Reminders set every *{intervals[minutes]}*!\n\n"
        "You'll receive updates about iFart Token Mini App.\n\n"
        "Use *Stop Reminders* to cancel.",
        parse_mode="Markdown",
    )

async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    try:
        user_id = job.data["user_id"]
        minutes = job.data["minutes"]
        content = await get_google_doc_content()
        await context.bot.send_message(
            chat_id=job.chat_id,
            text=f"🔔 *iFart Token Reminder*\n\n{content}\n\n⏰ Next reminder in {minutes} minutes",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Reminder error: {e}")
        user_id = job.data["user_id"]
        if user_id in user_jobs:
            for j in user_jobs[user_id]:
                j.schedule_removal()
            del user_jobs[user_id]

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🤖 *iFart Token Mini App Bot Help*\n\n"
        "/start - Begin with the bot\n"
        "/stop - Cancel all reminders\n"
        "/help - Show this message\n\n"
        "Use buttons to set reminder intervals.",
        parse_mode="Markdown",
    )

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in user_jobs:
        for job in user_jobs[user_id]:
            job.schedule_removal()
        del user_jobs[user_id]
        await update.message.reply_text("✅ All reminders stopped.")
    else:
        await update.message.reply_text("ℹ️ No active reminders.")

def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
