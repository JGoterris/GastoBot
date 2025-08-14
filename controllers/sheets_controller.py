from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, CallbackQueryHandler
from services.GenaiService import GenaiService
from services.SheetsService import SheetsService
from utils.auth import authorized_only
from utils.JsonUtil import json_fuller, json_formatter, to_list
from utils.Routes import Routes
from gspread.spreadsheet import Spreadsheet
import os
from utils.MenuTemplate import MenuTemplate


class SheetsController:
    def __init__(self, sheet_service: SheetsService, genai_service: GenaiService):
        self.sheet_service = sheet_service
        self.genai_service = genai_service

    @authorized_only
    async def text_request(self, update: Update, context = ContextTypes.DEFAULT_TYPE):
        str_json = self.genai_service.basic_request(update.message.text)
        fulled_json = json_fuller(str_json)
        formatted_json = "🧾 **REVISIÓN DE GASTO** 🧾\n\n" + json_formatter(fulled_json)
        context.user_data["json"] = fulled_json
        await update.message.reply_text(formatted_json, parse_mode="MARKDOWN", reply_markup=MenuTemplate.basic_menu())

    @authorized_only
    async def audio_request(self, update: Update, context = ContextTypes.DEFAULT_TYPE):
        try:
            voice_file = await update.message.voice.get_file()
            
            temp_path = f"temp_voice_{update.message.voice.file_id}.ogg"
            await voice_file.download_to_drive(temp_path)
            
            result = self.genai_service.audio_request(temp_path)
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            fulled_json = json_fuller(result)
            formatted_json = "🧾 **REVISIÓN DE GASTO** 🧾\n\n" + json_formatter(fulled_json)
            context.user_data["json"] = fulled_json
            await update.message.reply_text(formatted_json, parse_mode="MARKDOWN", reply_markup=MenuTemplate.basic_menu())
                
        except Exception as e:
            print(f"Error manejando voz: {e}")
            await update.message.reply_text("Ocurrió un error procesando tu mensaje de voz.")

    @authorized_only
    async def image_request(self, update: Update, context=ContextTypes.DEFAULT_TYPE):
        try:
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()

            temp_path = f"temp_photo_{photo.file_id}.jpg"
            await photo_file.download_to_drive(temp_path)

            result = self.genai_service.image_request(temp_path)

            if os.path.exists(temp_path):
                os.remove(temp_path)

            fulled_json = json_fuller(result)
            formatted_json = "🧾 **REVISIÓN DE GASTO** 🧾\n\n" + json_formatter(fulled_json)

            context.user_data["json"] = fulled_json
            await update.message.reply_text(formatted_json, parse_mode="MARKDOWN", reply_markup=MenuTemplate.basic_menu())

        except Exception as e:
            print(f"Error manejando imagen: {e}")
            await update.message.reply_text("Ocurrió un error procesando tu imagen.")

    
    @authorized_only
    async def submit_gasto(self, update: Update, context = CallbackContext):
        json_data = context.user_data["json"]
        self.sheet_service.upload_new_row(json_data)
        formatted_json = "🧾 **GASTO** 🧾\n\n" + json_formatter(json_data) + "\n\n✅ Subido"
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(formatted_json, parse_mode="MARKDOWN")
