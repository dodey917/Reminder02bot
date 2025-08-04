import logging
from datetime import timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    JobQueue,
)
from shared.database import Database

class ReminderBot:
    def __init__(self, token):
        self.app = Application.builder().token(token).build()
        self.db = Database()
        self.user_jobs = {}
        self._setup_handlers()

    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("stop", self.stop_command))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("10 min", callback_data="10"),
             InlineKeyboardButton("30 min", callback_data="30"),
             InlineKeyboardButton("1 hour", callback_data="60")],
            [InlineKeyboardButton("Stop", callback_data="stop")]
        ]
        await update.message.reply_text(
            "Set reminder interval:",
            reply_markup=InlineKeyboardMarkup(keyboard)
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        
        if query.data == "stop":
            if user_id in self.user_jobs:
                for job in self.user_jobs[user_id]:
                    job.schedule_removal()
                del self.user_jobs[user_id]
            await query.edit_message_text("✅ Reminders stopped")
            return
        
        try:
            minutes = int(query.data)
            if user_id in self.user_jobs:
                for job in self.user_jobs[user_id]:
                    job.schedule_removal()
            
            job = context.job_queue.run_repeating(
                self.send_reminder,
                interval=timedelta(minutes=minutes),
                first=timedelta(seconds=5),
                chat_id=query.message.chat_id,
                user_id=user_id,
                data=minutes
            )
            self.user_jobs[user_id] = [job]
            await query.edit_message_text(f"🔔 Reminders set every {minutes} minutes")
        except ValueError:
            await query.edit_message_text("⚠️ Invalid selection")

    async def send_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        job = context.job
        try:
            message = self.db.get_latest_message() or "Default reminder message"
            await context.bot.send_message(
                chat_id=job.chat_id,
                text=f"🔔 Reminder:\n\n{message}"
            )
        except Exception as e:
            logging.error(f"Reminder error: {e}")

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id in self.user_jobs:
            for job in self.user_jobs[user_id]:
                job.schedule_removal()
            del self.user_jobs[user_id]
            await update.message.reply_text("✅ All reminders stopped")
        else:
            await update.message.reply_text("ℹ️ No active reminders")

    def run(self):
        self.app.run_polling()
