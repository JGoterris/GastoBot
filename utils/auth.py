import os
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode


def authorized_only(func):
    """
    Decorador que restringe el uso de comandos solo al usuario autorizado.
    El ID del usuario autorizado debe estar en la variable de entorno MY_USER_ID.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        username = update.effective_user.username or "Sin username"
        
        authorized_user_id = int(os.getenv("MY_USER_ID", "0"))
        
        if authorized_user_id == 0:
            print("⚠️  WARNING: MY_USER_ID no está configurado en .env")
            await update.message.reply_text("❌ Bot no configurado correctamente.")
            return
        
        if user_id != authorized_user_id:
            print(f"🚫 Usuario no autorizado: {user_name} (@{username}) - ID: {user_id}")
            await update.message.reply_text("❌ Este bot es privado. No tienes permisos para usarlo.")
            return
        
        # Usuario autorizado - continuar con la función original
        print(f"✅ Usuario autorizado: {user_name} (@{username}) - ID: {user_id}")
        return await func(update, context)
    
    return wrapper


async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Función helper para obtener el ID del usuario.
    Usar temporalmente para conocer tu ID de usuario.
    """
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    username = update.effective_user.username or "Sin username"
    
    message = f"""
        🆔 **Tu información de usuario:**

        • *ID:* `{user_id}`
        • *Nombre:* {user_name}
        • *Username:* @{username}

        💡 *Para usar este bot:*
        1. Copia tu ID: `{user_id}`
        2. Agrégalo a tu archivo .env como: `MY_USER_ID={user_id}`
        3. Reinicia el bot
    """
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    print(f"📋 ID solicitado por: {user_name} (@{username}) - ID: {user_id}")