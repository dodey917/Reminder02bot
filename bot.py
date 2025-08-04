import os
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    JobQueue,
)
import httpx
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
TELEGRAM_TOKEN = "8132609297:AAGEbi5QRXfg_Bzs9a2SnqDyE-PKZPHkP3k"
GOOGLE_DOC_ID = "1wodxtiMwKBadOd8DoZpFccyqbMWRRCB8GgUEL-dFJHY"

# Google API credentials from the JSON file
SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "reminder02",
    "private_key_id": "4c1d4ae61d8687084fff41d6227a7cad6e4c6eb2",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDQ97AGR+/l8qgx
5CNRGklxkxhm8SU9gnPrNYKITvZaW2PZ4FD/Qbt/8CoTtI9vw4wz6sbbh0Irs6+Q
J9L7z+i5LVTQQ2UfVgTNFYj6lJXP1wm+KtC5H9OMS01JKheTV8aQLDhsHUOSY7hY
MoTybS8q0GrEE7uvdvK0+WlJevUQXTCrftZl4GAC340rOWE+XKl8nHrnFlMsks0r
XKfdFQYCQSmwJoAa60lKRkbKgpWcXsFTGiwGuMwTRhn/CIDMZRd4y+aYDN2RxvkM
DTRb3/SJe88uI+0APhocX25HIiy2vKGV49hOedvAjTN3L1vA5atiqUOJpr3xr9sP
ytEChxV7AgMBAAECggEARXuucJA38SZsDdbVdXC/rf+itAwH/XlkkPekdS2IVcgg
ngAr/ow9S8+wNggqT5fehR7SS4mgk4Z2YIEVcvyRXg14L53RQIeqJgU8nFGOtOLE
TxLOf1fZUENzqdnQqAIeOK8zfaOHZeQ5lj4KHc/3SI2vio4jMLdlAY8TFsdHOE6i
YFfqvcztObifRIGkMJ27xPVkKrOZQhLTYYdVMC3SE+JWrci1Eg4S2GrdXqU/7YaO
Lf+ibHN+MLNDcPDexpAtHln9VdYVL4e4GrRvqAETXxpIGTZEOBVurTe/BFQxWBph
f0ETpqBV+WlO7Kt3/0urAzDfzl9E8yjzIazpZGHW3QKBgQDw9P6y4EWPgCztWN2w
T8C2bQM292yAmZxfW7RWrOrwFmiZ0ceZ2Sszt8jeVVPbFwHPWt1GA2nX6heNy+2v
WM4TNsMWftf/sTx1KrLD9j3S6LIEgi4KJ4ix+a+Xp8EUX/JmtpWEqYySI0GjbR5G
UEC+ItGt2BJwmJPcL6sLTKUYTQKBgQDeA27K0v8iOE0l1oSWpMCWBFMr1y8VQ4SP
HJo3pIN1iIyrzaAtX9Qgg+uWGnKhIwX0+fkM8ZyKLr6yNnkCOQ68PQRStJ+orqTS
krm2601C9cfzaC2HqCFObIQlWtK3f89u2rGyHeqnpuDCp5BDK7Nv+rzUUtnQvDVQ
eTm6YdrI5wKBgHnnOMQ+enKzIgeiIeYFMzYXyLySSK53CIml14LSULnOXHUVkKnh
GN49aL4y5Q2+ggfprHCzYWT+5ZOzTDid8QP/fItw+M4/WJreUzqY5YZCe22Ufr5c
aefArnlHQYORVw1n6hUHwjpc4+ROXDaue1K2QuZ0nj+gsY2AAETjLdMxAoGAWFQR
TkyoCRtRRk6UrcKahJTv6i9QoiscoDuG98BSNP7AyNGkeqj3ooAZyLx5ArcGdbLG
bWnrF+cFI64ccs/0ltvHzofiRaBGHykVDjuLn6pdhO/bvW8c4TC3Wo1J7IvDIZ2M
uQrCAzWXkppMAQ1v9ItTeT4FPtDCfWPdndO00d0CgYBvrjKRIe30B+FSB1yE7vIg
SKrySxuLCXNoU6W1Y/Ks3VUfJaY7Yr8dw+BJjWhwMG+O3jQQcUOcRbaUNWvrhQuT
hu8etnnQdbIfPxgj9H4G6+8TTSnjQQMZGcldP3nxdJ4oaQ0UdD/QBpv/aoHa82XD
/JG0u9wqvRuE0XVZxvez9Q==
-----END PRIVATE KEY-----""",
    "client_email": "bot-access@reminder02.iam.gserviceaccount.com",
    "client_id": "117146824938030014556",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bot-access%40reminder02.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Dictionary to store user jobs
user_jobs = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton("10 min ⏰", callback_data="10"),
            InlineKeyboardButton("30 min ⏰", callback_data="30"),
            InlineKeyboardButton("1 hour ⏰", callback_data="60"),
        ],
        [
            InlineKeyboardButton("Stop Reminders ❌", callback_data="stop"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Get content from Google Doc
    doc_content = await get_google_doc_content()
    welcome_message = (
        f"👋 Hello {user.mention_html()}! Welcome to the *iFart Token Mini App* Reminder Bot!\n\n"
        f"{doc_content}\n\n"
        "🚀 *Set your reminder interval below:*"
    )
    
    await update.message.reply_html(
        welcome_message,
        reply_markup=reply_markup
    )

async def get_google_doc_content() -> str:
    """Fetch content from the Google Doc."""
    try:
        # Authenticate with the service account
        credentials = service_account.Credentials.from_service_account_info(
            SERVICE_ACCOUNT_INFO,
            scopes=['https://www.googleapis.com/auth/documents.readonly']
        )
        
        # Build the Google Docs service
        service = build('docs', 'v1', credentials=credentials)
        
        # Get the document
        doc = service.documents().get(documentId=GOOGLE_DOC_ID).execute()
        
        # Extract text content
        content = []
        for element in doc.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for para_element in element['paragraph']['elements']:
                    if 'textRun' in para_element:
                        content.append(para_element['textRun']['content'])
        
        return "".join(content).strip() or "⚠️ Important: Whale 🐳 are coming, fill your bag now! Buy before presale ends!"
    except Exception as e:
        logger.error(f"Error fetching Google Doc: {e}")
        return "⚠️ Important: Whale 🐳 are coming, fill your bag now! Buy before presale ends!"

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    
    if query.data == "stop":
        # Cancel any existing jobs for this user
        if user_id in user_jobs:
            for job in user_jobs[user_id]:
                job.schedule_removal()
            del user_jobs[user_id]
            await query.edit_message_text(text="✅ Reminders stopped. Use /start to begin again.")
        else:
            await query.edit_message_text(text="ℹ️ No active reminders to stop.")
        return
    
    # Parse the minutes from callback data
    try:
        minutes = int(query.data)
    except ValueError:
        logger.error(f"Invalid callback data: {query.data}")
        return
    
    # Cancel any existing jobs for this user
    if user_id in user_jobs:
        for job in user_jobs[user_id]:
            job.schedule_removal()
    
    # Create a new job
    job = context.job_queue.run_repeating(
        send_reminder,
        interval=timedelta(minutes=minutes),
        first=timedelta(seconds=10),
        chat_id=chat_id,
        user_id=user_id,
        data=minutes,
        name=str(user_id)
    
    # Store the job
    user_jobs[user_id] = [job]
    
    # Update message
    intervals = {
        10: "10 minutes",
        30: "30 minutes",
        60: "1 hour"
    }
    await query.edit_message_text(
        text=f"🔔 Reminder set for every *{intervals[minutes]}*!\n\n"
             "You'll receive regular updates about iFart Token Mini App.\n\n"
             "Use the *Stop Reminders* button to cancel.",
        parse_mode="Markdown"
    )

async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the reminder message."""
    job = context.job
    user_id = job.user_id
    chat_id = job.chat_id
    
    # Get fresh content from Google Doc
    reminder_message = await get_google_doc_content()
    
    # Add some emoji and formatting
    formatted_message = (
        f"🔔 *iFart Token Mini App Reminder*\n\n"
        f"{reminder_message}\n\n"
        f"⏰ Next reminder in {job.data} minutes"
    )
    
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=formatted_message,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error sending reminder to user {user_id}: {e}")
        # Remove the job if there's an error (e.g., user blocked the bot)
        if user_id in user_jobs:
            for job in user_jobs[user_id]:
                job.schedule_removal()
            del user_jobs[user_id]

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message."""
    help_text = (
        "🤖 *iFart Token Mini App Reminder Bot Help*\n\n"
        "/start - Begin interacting with the bot\n"
        "/stop - Stop all reminders\n"
        "/help - Show this help message\n\n"
        "Use the buttons to set reminder intervals for important updates."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop all reminders for the user."""
    user_id = update.effective_user.id
    if user_id in user_jobs:
        for job in user_jobs[user_id]:
            job.schedule_removal()
        del user_jobs[user_id]
        await update.message.reply_text("✅ All reminders have been stopped.")
    else:
        await update.message.reply_text("ℹ️ You don't have any active reminders.")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stop", stop_command))
    
    # Add callback handler for buttons
    application.add_handler(CallbackQueryHandler(button))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
