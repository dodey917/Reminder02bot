# ... [previous imports remain the same]

class DocsBot:
    # ... [previous methods remain the same]
    
    async def update_docs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Fetch and update content from Google Docs"""
        try:
            doc = self.docs_service.documents().get(
                documentId=self.config.GOOGLE_DOC_ID
            ).execute()
            
            content = []
            for element in doc.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for para in element['paragraph']['elements']:
                        if 'textRun' in para:
                            content.append(para['textRun']['content'])
            
            message = "".join(content).strip() or "⚠️ Important: Whale 🐳 are coming, fill your bag now!"
            self.db.save_message(message)
            
            await update.message.reply_text(
                "✅ iFart Token message updated from Google Docs!\n\n"
                f"Current message:\n\n{message}",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logging.error(f"Docs error: {e}")
            await update.message.reply_text("⚠️ Failed to update from Google Docs")
