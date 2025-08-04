# ... [previous imports remain the same]

class ReminderBot:
    # ... [previous methods remain the same]
    
    async def send_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send reminder message with current content"""
        job = context.job
        try:
            message = self.db.get_latest_message() or "⏰ Reminder: Don't forget about iFart Token!"
            await context.bot.send_message(
                chat_id=job.chat_id,
                text=f"🔔 *iFart Token Reminder*\n\n{message}\n\n"
                     f"Next reminder in {job.data} minutes",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Reminder error: {e}")
            if job.user_id in self.user_jobs:
                for j in self.user_jobs[job.user_id]:
                    j.schedule_removal()
                del self.user_jobs[job.user_id]
