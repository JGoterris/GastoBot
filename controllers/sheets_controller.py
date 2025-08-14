from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, CallbackQueryHandler
from services.GenaiService import GenaiService
from services.SheetsService import SheetsService
from utils.auth import authorized_only
from utils.JsonUtil import json_fuller, json_formatter, update_param
import os
from utils.MenuTemplate import MenuTemplate
import json
import re
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class SheetsController:
    def __init__(self, sheet_service: SheetsService, genai_service: GenaiService):
        self.sheet_service = sheet_service
        self.genai_service = genai_service

    async def _handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception, operation: str):
        error_msg = f"Error en {operation}: {str(error)}"
        logger.error(error_msg, exc_info=True)
        
        user_msg = (
            "❌ **Error** ❌\n\n"
            f"Ocurrió un problema al {operation}.\n"
            "Por favor, inténtalo de nuevo."
        )
        
        try:
            if update.message:
                await update.message.reply_text(user_msg, parse_mode="MARKDOWN")
            elif update.callback_query:
                await update.callback_query.message.reply_text(user_msg, parse_mode="MARKDOWN")
                await update.callback_query.answer()
        except Exception as reply_error:
            logger.error(f"Error enviando mensaje de error: {reply_error}")

    @authorized_only
    async def text_request(self, update: Update, context = ContextTypes.DEFAULT_TYPE):
        try:
            if context.user_data.get("waiting_for", None):
                await self.realizar_modificacion(update, context)
                return

            str_json = self.genai_service.basic_request(update.message.text)
            fulled_json = json_fuller(str_json)
            await self.revision_de_gasto(update, context, fulled_json)
        except Exception as e:
            await self._handle_error(update, context, e, "procesar mensaje de texto")

    @authorized_only
    async def audio_request(self, update: Update, context = ContextTypes.DEFAULT_TYPE):
        temp_path = None
        try:
            voice_file = await update.message.voice.get_file()
            
            temp_path = f"temp_voice_{update.message.voice.file_id}.ogg"
            await voice_file.download_to_drive(temp_path)
            
            result = self.genai_service.audio_request(temp_path)
            
            fulled_json = json_fuller(result)
            await self.revision_de_gasto(update, context, fulled_json)
                
        except Exception as e:
            await self._handle_error(update, context, e, "procesar mensaje de audio")
        
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    logger.error(f"Error eliminando archivo temporal {temp_path}: {e}")

    @authorized_only
    async def image_request(self, update: Update, context=ContextTypes.DEFAULT_TYPE):
        temp_path = None
        try:
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()

            temp_path = f"temp_photo_{photo.file_id}.jpg"
            await photo_file.download_to_drive(temp_path)

            result = self.genai_service.image_request(temp_path)

            fulled_json = json_fuller(result)
            await self.revision_de_gasto(update, context, fulled_json)

        except Exception as e:
            await self._handle_error(update, context, e, "procesar imagen")

        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    logger.error(f"Error eliminando archivo temporal {temp_path}: {e}")

    async def revision_de_gasto(self, update: Update, context: ContextTypes.DEFAULT_TYPE, json_data: str):
        try:
            context.user_data["json"] = json_data
            if not json_data:
                await update.callback_query.answer("❌ No hay datos de gasto para mostrar")
                return
            formatted_json = "🧾 **REVISIÓN DE GASTO** 🧾\n\n" + json_formatter(json_data)
            await update.message.reply_text(formatted_json, parse_mode="MARKDOWN", reply_markup=MenuTemplate.basic_menu())
        except Exception as e:
            await self._handle_error(update, context, e, "mostrar revisión de gasto")

    @authorized_only
    async def submit_gasto(self, update: Update, context = CallbackContext):
        try:
            json_data = context.user_data["json"]
            if not json_data:
                await update.callback_query.answer("❌ No hay datos de gasto para subir")
                return
            self.sheet_service.upload_new_row(json_data)
            formatted_json = "🧾 **GASTO** 🧾\n\n" + json_formatter(json_data) + "\n\n✅ Subido"
            context.user_data["json"] = None
            await update.callback_query.answer("✅ Gasto guardado correctamente")
            await update.callback_query.message.edit_text(formatted_json, parse_mode="MARKDOWN")
        except Exception as e:
            await self._handle_error(update, context, e, "guardar gasto")
            await update.callback_query.answer("❌ Error al guardar el gasto")

    @authorized_only
    async def cancelar_gasto(self, update: Update, context = CallbackContext):
        try:
            json_data = context.user_data["json"]
            if not json_data:
                await update.callback_query.answer("❌ No hay datos de gasto para cancelar")
                return
            formatted_json = "🧾 **GASTO** 🧾\n\n" + json_formatter(json_data) + "\n\n❌ Cancelado"
            context.user_data["json"] = None
            await update.callback_query.answer("❌ Gasto cancelado")
            await update.callback_query.message.edit_text(formatted_json, parse_mode="MARKDOWN")
        except Exception as e:
            await self._handle_error(update, context, e, "cancelar gasto")
            await update.callback_query.answer("❌ Error al cancelar")

    @authorized_only
    async def modify_gasto(self, update: Update, context = CallbackContext):
        try:
            context.user_data["waiting_for"] = None
            json_data = context.user_data["json"]
            if not json_data:
                await update.callback_query.answer("❌ No hay datos de gasto para modificar")
                return
            texto = "✏️ ¿Qué quieres modificar? ✏️\n\n" + json_formatter(json_data)
            await update.callback_query.message.edit_text(texto, parse_mode="MARKDOWN", reply_markup=MenuTemplate.parameters_menu())
        except Exception as e:
            await self._handle_error(update, context, e, "mostrar opciones de modificación")
            await update.callback_query.answer("❌ Error al abrir modificaciones")

    @authorized_only
    async def modify_establecimiento(self, update: Update, context = CallbackContext):
        try:
            json_str = context.user_data["json"]
            if not json_str:
                await update.callback_query.answer("❌ No hay datos de gasto")
                return
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
        except json.JSONDecodeError:
            await update.callback_query.answer("❌ Error en los datos del gasto")
        except Exception as e:
            await self._handle_error(update, context, e, "modificar establecimiento")
            await update.callback_query.answer("❌ Error al modificar establecimiento")

    @authorized_only
    async def modify_importe(self, update: Update, context: CallbackContext):
        try:
            json_str = context.user_data["json"]
            if not json_str:
                    await update.callback_query.answer("❌ No hay datos de gasto")
                    return
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
        except json.JSONDecodeError:
            await update.callback_query.answer("❌ Error en los datos del gasto")
        except Exception as e:
            await self._handle_error(update, context, e, "modificar importe")
            await update.callback_query.answer("❌ Error al modificar importe")

    @authorized_only
    async def modify_descripcion(self, update: Update, context: CallbackContext):
        try:
            json_str = context.user_data["json"]
            if not json_str:
                    await update.callback_query.answer("❌ No hay datos de gasto")
                    return
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
        except json.JSONDecodeError:
            await update.callback_query.answer("❌ Error en los datos del gasto")
        except Exception as e:
            await self._handle_error(update, context, e, "modificar descripción")
            await update.callback_query.answer("❌ Error al modificar descripción")
    
    @authorized_only
    async def modify_fecha(self, update: Update, context: CallbackContext):
        try:
            json_str = context.user_data["json"]
            if not json_str:
                    await update.callback_query.answer("❌ No hay datos de gasto")
                    return
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
        except json.JSONDecodeError:
            await update.callback_query.answer("❌ Error en los datos del gasto")
        except Exception as e:
            await self._handle_error(update, context, e, "modificar fecha")
            await update.callback_query.answer("❌ Error al modificar fecha")

    @authorized_only
    async def modify_categoria(self, update: Update, context: CallbackContext):
        try:
            json_str = context.user_data["json"]
            if not json_str:
                    await update.callback_query.answer("❌ No hay datos de gasto")
                    return
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
        except json.JSONDecodeError:
            await update.callback_query.answer("❌ Error en los datos del gasto")
        except Exception as e:
            await self._handle_error(update, context, e, "modificar categoría")
            await update.callback_query.answer("❌ Error al modificar categoría")
    
    async def realizar_modificacion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            waiting_for = context.user_data["waiting_for"]
            json_str_data = context.user_data["json"]
            if not waiting_for or not json_str_data:
                await update.message.reply_text("❌ No hay modificación pendiente.")
                return
            texto = update.message.text.strip()
            match waiting_for:
                case "importe":
                    if not re.fullmatch(r"\d+(\.\d{1,2})?", texto):
                        await update.message.reply_text(
                            "❌ **Formato inválido**\n\n"
                            "El importe debe tener formato: `123` o `123.45`\n"
                            "Usa punto como separador decimal.",
                            parse_mode="MARKDOWN"
                        )
                    json_str_data = update_param(json_str_data, "importe", texto)
                    await update.message.reply_text(f"✅ Importe actualizado a {texto} €")
                    
                case "fecha":
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto):
                        await update.message.reply_text(
                            "❌ **Formato inválido**\n\n"
                            "La fecha debe tener formato: `YYYY-MM-DD`\n"
                            "Ejemplo: `2024-03-15`",
                            parse_mode="MARKDOWN"
                        )
                        return
                    json_str_data = update_param(json_str_data, "fecha", texto)
                    await update.message.reply_text(f"✅ Fecha actualizada a {texto}")
                case _:
                    json_str_data = update_param(json_str_data, waiting_for, texto)
                    await update.message.reply_text(f"✅ {str(waiting_for).capitalize()} actualizada a {texto}")
            context.user_data["json"] = json_str_data
            context.user_data["waiting_for"] = None
            await self.revision_de_gasto(update, context, json_str_data)
        except Exception as e:
            await self._handle_error(update, context, e, "realizar modificación")

    @authorized_only
    async def volver_menu(self, update: Update, context = CallbackContext):
        try:
            json_data = context.user_data["json"]
            if not json_data:
                await update.callback_query.answer("❌ No hay datos de gasto")
                return
            formatted_json = "🧾 **REVISIÓN DE GASTO** 🧾\n\n" + json_formatter(json_data)
            await update.callback_query.message.edit_text(formatted_json, parse_mode="MARKDOWN", reply_markup=MenuTemplate.basic_menu())   
        except Exception as e:
            await self._handle_error(update, context, e, "volver al menú")
            await update.callback_query.answer("❌ Error al volver al menú")

    @authorized_only
    async def summary(self, update: Update, context = ContextTypes.DEFAULT_TYPE):
        try:
            summary_data = self.sheet_service.get_monthly_summary()
            
            if not summary_data:
                await update.message.reply_text(
                    "📊 **RESUMEN MENSUAL** 📊\n\n"
                    "No hay datos disponibles para este mes.",
                    parse_mode="MARKDOWN"
                )
                return

            await update.message.reply_text(summary_data, parse_mode="MARKDOWN")    
        except Exception as e:
            await self._handle_error(update, context, e, "generar resumen mensual")

    @authorized_only
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
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
        except Exception as e:
            await self._handle_error(update, context, e, "mostrar mensaje de bienvenida")

    @authorized_only
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
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
        except Exception as e:
            await self._handle_error(update, context, e, "mostrar mensaje de ayuda")