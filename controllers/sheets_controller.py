from telegram import Update
from telegram.ext import ContextTypes
from services.GenaiService import GenaiService
from services.SheetsService import SheetsService
from utils.auth import authorized_only


class SheetsController:
    def __init__(self, sheets_service: SheetsService, genai_service: GenaiService):
        self.sheets_service = sheets_service
        self.genai_service = genai_service

    @authorized_only
    async def say_hello(self, update: Update, context = ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hola mundo!")