import os
import random
from threading import Timer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Bot tokens
BOT_TOKENS = [
    "8229670972:AAFAxmQMxM0Vkfu5s_Gl73GsY4K3qwZ3p8E",  # Bot 1
    "8132609297:AAGEbi5QRXfg_Bzs9a2SnqDyE-PKZPHkP3k",  # Bot 2
    "8404435003:AAG6ePF9lNjozAk40hcep8jUXq8w-qzZ9KY"   # Bot 3
]

# Reminder messages
REMINDER_MESSAGES = [
    "⏰ Buy now before presale ends! Whale 🐳 are coming, fill your bag now!",
    "🚨 Don't miss out! Presale ending soon - whales are accumulating!",
    "💰 Last chance to buy before price pumps! Fill your bags!",
    "🐳 Whales are buying! Don't be left behind - buy now!",
    "🔥 Hot opportunity! Presale ending soon - get in before it's too late!",
    "🚀 Rocket fuel loading! Buy now before takeoff!",
    "💎 Diamond hands win! Accumulate before the surge!",
    "📈 Charts looking bullish! Time to fill your bags!",
    "🤑 Don't regret later - buy now before price explodes!",
    "⚡ Lightning deal! Last chance before presale closes!"
]

# Store active reminders for each chat
active_reminders = {}

def start(update: Update, context: CallbackContext) -> None:
    """Send a message with the inline keyboard when the command /start is issued."""
    keyboard = [
        [
            InlineKeyboardButton("10 min", callback_data='10'),
            InlineKeyboardButton("30 min", callback_data='30'),
            InlineKeyboardButton("1 hour", callback_data='60'),
        ],
        [InlineKeyboardButton("Stop Reminders", callback_data='stop')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        'Please choose a reminder interval:',
        reply_markup=reply_markup
    )

def button(update: Update, context: CallbackContext) -> None:
    """Handle button presses."""
    query = update.callback_query
    query.answer()
    
    chat_id = query.message.chat_id
    data = query.data
    
    if data == 'stop':
        # Stop any existing reminders for this chat
        if chat_id in active_reminders:
            for timer in active_reminders[chat_id]:
                timer.cancel()
            del active_reminders[chat_id]
        query.edit_message_text(text="Reminders stopped!")
        return
    
    # Convert minutes to seconds
    interval = int(data) * 60
    
    # Stop any existing reminders for this chat
    if chat_id in active_reminders:
        for timer in active_reminders[chat_id]:
            timer.cancel()
    
    # Create new reminder
    active_reminders[chat_id] = []
    timer = RepeatedTimer(interval, send_reminder, context.bot, chat_id)
    active_reminders[chat_id].append(timer)
    
    query.edit_message_text(text=f"Reminders started! Interval: {data} minutes")

def send_reminder(bot, chat_id):
    """Send a random reminder message to the chat."""
    message = random.choice(REMINDER_MESSAGES)
    bot.send_message(chat_id=chat_id, text=message)

class RepeatedTimer:
    """A timer that repeats at a given interval."""
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        """Start the timer."""
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def cancel(self):
        """Cancel the timer."""
        self._timer.cancel()
        self.is_running = False

def error_handler(update: Update, context: CallbackContext) -> None:
    """Log errors."""
    print(f'Update {update} caused error {context.error}')

def main() -> None:
    """Start all three bots."""
    for i, token in enumerate(BOT_TOKENS, 1):
        # Create the Updater and pass it your bot's token.
        updater = Updater(token)
        
        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher
        
        # Register command and button handlers
        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(CallbackQueryHandler(button))
        dispatcher.add_error_handler(error_handler)
        
        # Start the Bot
        updater.start_polling()
        
        print(f"Bot {i} is running...")
    
    # Run all bots until Ctrl-C is pressed
    for updater in updater._dispatcher.updater:
        updater.idle()

if __name__ == '__main__':
    main()
