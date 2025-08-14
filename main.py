from dotenv import load_dotenv
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from services.SheetsService import SheetsService
from controllers.sheets_controller import SheetsController
import utils.auth as auth
from services.GenaiService import GenaiService
from utils.Routes import Routes

# Cargar variables de entorno
load_dotenv()

def check_environment():
    # Verificar que todas las variables de entorno estén configuradas
    required_vars = ["TOKEN_BOT", "SHEET_ID", "MY_USER_ID", "GEMINI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ ERROR: Variables faltantes en .env: {', '.join(missing_vars)}")
        print("\n📝 Tu archivo .env debe contener:")
        print("TOKEN_BOT=tu_token_de_telegram")
        print("SHEET_ID=tu_id_de_google_sheets")
        print("MY_USER_ID=tu_id_de_usuario")
        print("GEMINI_API_KEY=tu_api_key_de_gemini")
        print("\n💡 Usa el comando /myid para obtener tu ID de usuario")
        return False
    
    print("✅ Todas las variables de entorno están configuradas")
    return True

def initialize_sheets_service():
    try:
        print("🔗 Conectando con Google Sheets...")
        sheet_service = SheetsService("creds.json", os.getenv("SHEET_ID"))
        print("✅ Conexión con Google Sheets establecida")
        return sheet_service
    except FileNotFoundError:
        print("❌ ERROR: Archivo creds.json no encontrado")
        print("💡 Asegúrate de tener el archivo de credenciales de Google en la raíz del proyecto")
        return None
    except Exception as e:
        print(f"❌ ERROR: No se pudo conectar con Google Sheets: {e}")
        return None

def initialize_genai_service():
    try:
        print("🔗 Creando genai")
        genai = GenaiService()
        print("✅ Cliente genai creado")
        return genai
    except Exception as e:
        print(f"❌ ERROR: No se pudo crear el cliente genai")
        return None

def setup_handlers(application, sheets_controller: SheetsController):
    """Configurar todos los handlers del bot"""
        
    application.add_handler(CommandHandler("myid", auth.get_user_id))
    application.add_handler(CommandHandler("start", sheets_controller.start))
    application.add_handler(CommandHandler("help", sheets_controller.help))

    # Funcionamiento principal
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, sheets_controller.text_request))
    application.add_handler(MessageHandler(filters.VOICE, sheets_controller.audio_request))
    application.add_handler(MessageHandler(filters.PHOTO, sheets_controller.image_request))
    application.add_handler(CallbackQueryHandler(sheets_controller.submit_gasto, pattern=Routes.P_ACEPTAR))
    application.add_handler(CallbackQueryHandler(sheets_controller.modify_gasto, pattern=Routes.P_MODIFICAR))
    application.add_handler(CallbackQueryHandler(sheets_controller.cancelar_gasto, pattern=Routes.P_CANCELAR))
    application.add_handler(CommandHandler("summary", sheets_controller.summary))

    # Modificaciones
    application.add_handler(CallbackQueryHandler(sheets_controller.modify_establecimiento, pattern=Routes.P_MODIFICAR_ESTABLECIMIENTO))
    application.add_handler(CallbackQueryHandler(sheets_controller.modify_importe, pattern=Routes.P_MODIFICAR_IMPORTE))
    application.add_handler(CallbackQueryHandler(sheets_controller.modify_descripcion, pattern=Routes.P_MODIFICAR_DESCRIPCION))
    application.add_handler(CallbackQueryHandler(sheets_controller.modify_fecha, pattern=Routes.P_MODIFICAR_FECHA))
    application.add_handler(CallbackQueryHandler(sheets_controller.modify_categoria, pattern=Routes.P_MODIFICAR_CATEGORIA))
    application.add_handler(CallbackQueryHandler(sheets_controller.modify_gasto, pattern=Routes.P_ATRAS_MODIFICACIONES))
    application.add_handler(CallbackQueryHandler(sheets_controller.volver_menu, pattern=Routes.P_VOLVER_MENU))
    
    print("✅ Todos los handlers configurados")

def main():
    # Función principal del bot
    print("🚀 Iniciando GastoBot...")
    print("=" * 50)
    
    # 1. Verificar configuración
    if not check_environment():
        exit(1)
    
    # 2. Inicializar servicios
    sheet_service = initialize_sheets_service()
    genai_service = initialize_genai_service()
    if not sheet_service or not genai_service:
        exit(1)
    
    # 2.1 Instanciar controladores
    sheets_controller = SheetsController(sheet_service, genai_service)

    # 3. Crear aplicación de Telegram
    try:
        application = ApplicationBuilder().token(os.getenv("TOKEN_BOT")).build()
        print("✅ Aplicación de Telegram creada")
    except Exception as e:
        print(f"❌ ERROR: No se pudo crear la aplicación de Telegram: {e}")
        exit(1)
    
    # 4. Configurar handlers
    setup_handlers(application, sheets_controller)
    
    # 5. Mostrar información de inicio
    print("=" * 50)
    print("🤖 Bot configurado correctamente")
    print(f"📱 Usuario autorizado: {os.getenv('MY_USER_ID')}")
    print("💡 Comandos disponibles: /start, /myid")
    print("⚠️  Recuerda eliminar el comando /myid después de configurar")
    print("⏹️  Presiona Ctrl+C para detener el bot")
    print("=" * 50)
    
    # 6. Iniciar bot
    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("\n👋 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando el bot: {e}")

if __name__ == "__main__":
    main()