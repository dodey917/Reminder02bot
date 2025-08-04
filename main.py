import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import asyncio
from bots.reminder_bot import ReminderBot
from bots.docs_bot import DocsBot
from shared.config import Config
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def main():
    config = Config()
    
    logging.info("Starting both bots...")
    reminder_bot = ReminderBot(config.REMINDER_BOT_TOKEN)
    docs_bot = DocsBot(config.DOCS_BOT_TOKEN)
    
    # Initial message update
    try:
        # Initialize docs service to get first message
        docs_bot._setup_google_client()
        doc = docs_bot.docs_service.documents().get(
            documentId=config.GOOGLE_DOC_ID
        ).execute()
        
        content = []
        for element in doc.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for para in element['paragraph']['elements']:
                    if 'textRun' in para:
                        content.append(para['textRun']['content'])
        
        message = "".join(content).strip() or "Default reminder message"
        docs_bot.db.save_message(message)
        logging.info("Initial message loaded from Google Docs")
    except Exception as e:
        logging.error(f"Initial docs load failed: {e}")
    
    # Run both bots
    await asyncio.gather(
        reminder_bot.app.run_polling(),
        docs_bot.app.run_polling()
    )

if __name__ == "__main__":
    asyncio.run(main())
