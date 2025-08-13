from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, CallbackQueryHandler
from services.GenaiService import GenaiService
from utils.auth import authorized_only
from utils.JsonUtil import json_fuller, json_formatter, to_list
from Routes import Routes
from gspread.spreadsheet import Spreadsheet


class SheetsController:
    def __init__(self, sheet: Spreadsheet, genai_service: GenaiService):
        self.sheet = sheet
        self.genai_service = genai_service

    @authorized_only
    async def text_request(self, update: Update, context = ContextTypes.DEFAULT_TYPE):
        str_json = self.genai_service.basic_request(update.message.text)
        fulled_json = json_fuller(str_json)
        formated_json = json_formatter(fulled_json)
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="✅ Aceptar", callback_data=Routes.ACEPTAR)
            ],
            [
                InlineKeyboardButton(text="✏️ Modificar", callback_data=Routes.MODIFICAR)
            ]
        ])
        context.user_data["json"] = fulled_json
        await update.message.reply_text(formated_json, parse_mode="MARKDOWN", reply_markup=keyboard)
    
    @authorized_only
    async def submit_gasto(self, update: Update, context = CallbackContext):
        json_data = context.user_data["json"]
        worksheet = self.sheet.get_worksheet(0)
        worksheet.append_row(to_list(json_data))
        await update.callback_query.answer()
