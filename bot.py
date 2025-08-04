from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import random

TOKEN = "8132609297:AAGEbi5QRXfg_Bzs9a2SnqDyE-PKZPHkP3k"

# List of reminder messages with occasional links
REMINDER_MESSAGES = [
    "iFart Token's deflationary model rewards holders! Buy now 🚀",
    "Don't be late - whales are accumulating $iFART! 🐳",
    "Play the iFart Mini-App to earn tokens! Official Links: Mini-App | Buy $iFART",
    "3% transaction tax: 1.5% burned, 1.5% to LP - iFart's smart tokenomics",
    "iFart Token: Combining memes with real utility. Official Links: Mini-App | Buy $iFART",
    "Phase 2 coming soon - mobile app and DEX launch! Stay tuned 📱"
]

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ['10min', '30min'],
        ['1hr', 'Stop']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text('iFart Reminder Bot 2 ready! Choose interval:', reply_markup=reply_markup)

def send_reminder(context: CallbackContext):
    job = context.job
    message = random.choice(REMINDER_MESSAGES)
    context.bot.send_message(job.context, text=message)

def handle_message(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    text = update.message.text.lower()
    
    if text == 'stop':
        current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
        for job in current_jobs:
            job.schedule_removal()
        update.message.reply_text("Reminders stopped!")
        return
    
    if text not in ['10min', '30min', '1hr']:
        return
    
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
    
    interval = 600 if text == '10min' else 1800 if text == '30min' else 3600
    
    context.job_queue.run_repeating(
        send_reminder, 
        interval, 
        first=5,
        context=chat_id, 
        name=str(chat_id)
    )
    update.message.reply_text(f"iFart reminders started every {text}!")

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
