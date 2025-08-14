from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, CallbackQueryHandler
from services.GenaiService import GenaiService
from services.SheetsService import SheetsService
from utils.auth import authorized_only
from utils.JsonUtil import json_fuller, json_formatter, to_list
import os
from utils.MenuTemplate import MenuTemplate
import json
import re


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
        context.user_data["json"] = None
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(formatted_json, parse_mode="MARKDOWN")
    
    @authorized_only
    async def modify_gasto(self, update: Update, context = CallbackContext):
        context.user_data["waiting_for"] = None
        json_data = context.user_data["json"]
        texto = "✏️ ¿Qué quieres modificar? ✏️\n\n" + json_formatter(json_data)
        await update.callback_query.message.edit_text(texto, parse_mode="MARKDOWN", reply_markup=MenuTemplate.parameters_menu())

    @authorized_only
    async def modify_establecimiento(self, update: Update, context = CallbackContext):
        json_str = context.user_data["json"]
        json_data = json.loads(json_str)
        establecimiento_actual = json_data.get("establecimiento", "No especificado")
        texto = (
            f"✏️ **MODIFICANDO ESTABLECIMIENTO** ✏️\n\n"
            f"📍 **Actual**: {establecimiento_actual}\n\n"
            f"💬 Escribe el nuevo establecimiento:"
        )

        context.user_data["waiting_for"] = "establecimiento"

        await update.callback_query.message.edit_text(
                    texto, 
                    parse_mode="MARKDOWN",
                    reply_markup=MenuTemplate.volver_atras_a_modificaciones()
                )
        
        await update.callback_query.answer()

    @authorized_only
    async def modify_importe(self, update: Update, context: CallbackContext):
        json_str = context.user_data["json"]
        json_data = json.loads(json_str)
        importe_actual = json_data.get("importe", "No especificado")
        texto = (
            f"✏️ **MODIFICANDO IMPORTE** ✏️\n\n"
            f"🏷️ **Actual**: {importe_actual}\n\n"
            f"💬 Escribe el nuevo importe en formato `123.45` (punto como separador decimal):"
        )
        
        context.user_data["waiting_for"] = "importe"
            
        await update.callback_query.message.edit_text(
            texto, 
            parse_mode="MARKDOWN",
            reply_markup=MenuTemplate.volver_atras_a_modificaciones()
        )
        await update.callback_query.answer()

    @authorized_only
    async def modify_descripcion(self, update: Update, context: CallbackContext):
        json_str = context.user_data["json"]
        json_data = json.loads(json_str)
        descripcion_actual = json_data.get("descripcion", "No especificado")
        texto = (
            f"✏️ **MODIFICANDO DESCRIPCION** ✏️\n\n"
            f"🏷️ **Actual**: {descripcion_actual}\n\n"
            f"💬 Escribe la nueva descripción:"
        )
        
        context.user_data["waiting_for"] = "descripcion"
            
        await update.callback_query.message.edit_text(
            texto, 
            parse_mode="MARKDOWN",
            reply_markup=MenuTemplate.volver_atras_a_modificaciones()
        )
        await update.callback_query.answer()
    
    @authorized_only
    async def modify_fecha(self, update: Update, context: CallbackContext):
        json_str = context.user_data["json"]
        json_data = json.loads(json_str)
        fecha_actual = json_data.get("fecha", "No especificado")
        texto = (
            f"✏️ **MODIFICANDO FECHA** ✏️\n\n"
            f"🏷️ **Actual**: {fecha_actual}\n\n"
            f"💬 Escribe la nueva fecha en formato YYYY-MM-DD:"
        )
        
        context.user_data["waiting_for"] = "fecha"
            
        await update.callback_query.message.edit_text(
            texto, 
            parse_mode="MARKDOWN",
            reply_markup=MenuTemplate.volver_atras_a_modificaciones()
        )
        await update.callback_query.answer()

    @authorized_only
    async def modify_categoria(self, update: Update, context: CallbackContext):
        json_str = context.user_data["json"]
        json_data = json.loads(json_str)
        categoria_actual = json_data.get("categoria", "No especificada")
        texto = (
                f"✏️ **MODIFICANDO CATEGORÍA** ✏️\n\n"
                f"🏷️ **Actual**: {categoria_actual}\n\n"
                f"💬 Escribe la nueva categoría:"
            )
        
        context.user_data["waiting_for"] = "categoria"
            
        await update.callback_query.message.edit_text(
            texto, 
            parse_mode="MARKDOWN",
            reply_markup=MenuTemplate.volver_atras_a_modificaciones()
        )
        await update.callback_query.answer()

    @authorized_only
    async def summary(self, update: Update, context = ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(self.sheet_service.get_monthly_summary())
    
    @authorized_only
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_message = (
            "¡Bienvenido a GastoBot! 🤖💰\n\n"
            "Puedo ayudarte a registrar tus gastos de manera automática.\n\n"
            "📝 **¿Cómo funciona?**\n"
            "• Envíame un mensaje describiendo tu gasto\n"
            "• Envía una foto del ticket\n"
            "• Graba un audio con los detalles\n\n"
            "🔧 **Comandos disponibles:**\n"
            "• /summary - Ver resumen mensual\n"
            "• /help - Mostrar ayuda\n\n"
            "¡Empecemos! Envíame tu primer gasto 📊"
        )
        await update.message.reply_text(welcome_message, parse_mode="MARKDOWN")

    @authorized_only
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_message = (
            "🆘 **AYUDA - GastoBot** 🆘\n\n"
            "📤 **Formas de enviar gastos:**\n"
            "• **Texto**: 'Pagué 15€ en Mercadona por comida'\n"
            "• **Audio**: Graba un mensaje de voz\n"
            "• **Foto**: Sube una imagen del ticket\n\n"
            "⚙️ **Después de procesar:**\n"
            "• ✅ **Aceptar**: Guarda el gasto tal como está\n"
            "• ✏️ **Modificar**: Cambia algún campo antes de guardar\n\n"
            "📊 **Comandos:**\n"
            "• `/summary` - Resumen de gastos del mes\n"
            "• `/help` - Mostrar esta ayuda\n\n"
            "💡 **Tip**: Sé específico en tus descripciones para mejor precisión"
        )
        await update.message.reply_text(help_message, parse_mode="MARKDOWN")
