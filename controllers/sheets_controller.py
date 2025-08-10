from telegram import Update
from telegram.ext import ContextTypes
from utils.auth import authorized_only


class SheetsController:
    @staticmethod
    @authorized_only
    async def say_hello(update: Update, context = ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hola mundo!")