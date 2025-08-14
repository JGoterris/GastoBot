# GastoBot 🤖💰

GastoBot es un bot de Telegram diseñado para registrar tus gastos personales de forma rápida e inteligente. Utiliza la potencia de la IA generativa de Google para entender tus mensajes, audios o incluso fotos de tickets, y los convierte en entradas estructuradas en una hoja de cálculo de Google Sheets.

**El proyecto aún no es estable y tiene algunos bugs. Sigo trabajando para conseguir tener un bot confiable.**

## ✨ Features

- **Registro Inteligente**: Envía un mensaje de texto (`pagué 15€ en el super`), una nota de voz, o una foto de un ticket y el bot extraerá la información relevante.
- **Validación de Gastos**: Antes de guardar un gasto, puedes revisarlo, modificar cualquier campo (establecimiento, importe, descripción, etc.) o cancelarlo.
- **Organización Automática**: Los gastos se guardan en una Google Sheet, organizados automáticamente en hojas por mes (ej. "Agosto 2025").
- **Resúmenes Mensuales**: Usa el comando `/summary` para obtener un resumen de tus gastos del mes actual, desglosado por categorías.
- **Seguro**: El bot solo responde a tu usuario de Telegram, ignorando los mensajes de cualquier otra persona.

## ⚙️ Cómo Funciona

El flujo de trabajo del bot es el siguiente:

1.  **Recibe Input**: El usuario envía un mensaje de texto, voz o una imagen al bot en Telegram.
2.  **Procesa con IA**: El bot envía el input al modelo de IA Generativa de Google (Gemini), que extrae los detalles del gasto (establecimiento, importe, descripción y categoría) en un formato JSON.
3.  **Muestra para Revisión**: El bot presenta los datos extraídos al usuario en un menú interactivo.
4.  **Confirma o Modifica**: El usuario puede `Aceptar` el gasto, `Modificar` cualquiera de sus campos o `Cancelar` la operación.
5.  **Guarda en Google Sheets**: Una vez aceptado, el gasto se añade como una nueva fila en la hoja de cálculo correspondiente al mes actual.

## 🛠️ Tech Stack

- **Python**: Lenguaje principal.
- **python-telegram-bot**: Para la interacción con la API de Telegram.
- **Google Generative AI**: Para el procesamiento de lenguaje natural e imágenes (modelo Gemini).
- **gspread**: Para la interacción con la API de Google Sheets.
- **python-dotenv**: Para la gestión de variables de entorno.

## 🚀 Configuración

Sigue estos pasos para configurar y ejecutar tu propia instancia de GastoBot.

### 1. Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_DIRECTORIO>
```

### 2. Crear Entorno Virtual e Instalar Dependencias

Es recomendable usar un entorno virtual para aislar las dependencias del proyecto.

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar Google Cloud y Google Sheets

**a. Crear un Proyecto en Google Cloud:**
   - Ve a la [Consola de Google Cloud](https://console.cloud.google.com/) y crea un nuevo proyecto.

**b. Habilitar APIs:**
   - En tu proyecto, ve a la sección "APIs y Servicios" -> "Biblioteca".
   - Busca y habilita las siguientes APIs:
     1.  **Google Sheets API**

**c. Crear Credenciales de Cuenta de Servicio:**
   - Ve a "APIs y Servicios" -> "Credenciales".
   - Haz clic en "Crear credenciales" -> "Cuenta de servicio".
   - Dale un nombre a la cuenta de servicio (ej. `gastobot-sheets`) y haz clic en "Crear y continuar".
   - Otorga el rol de "Editor" para que pueda modificar tus Google Sheets.
   - Salta el último paso y haz clic en "Listo".
   - Una vez creada, ve a la pestaña "Claves" de la cuenta de servicio, haz clic en "Agregar clave" -> "Crear nueva clave".
   - Selecciona el tipo **JSON** y descárgala.
   - **Renombra el archivo descargado a `creds.json` y muévelo a la raíz de tu proyecto.**

**d. Crear una Google Sheet:**
   - Ve a [Google Sheets](https://sheets.google.com/create) y crea una nueva hoja de cálculo. (O hazlo desde tu panel de Google Drive)
   - **Comparte la hoja de cálculo con tu cuenta de servicio.** Para ello, haz clic en "Compartir" y pega el email de la cuenta de servicio (lo encontrarás en los detalles de la cuenta de servicio en la consola de Google Cloud). Dale permisos de "Editor".

### 4. Configurar Gemini

**a. Acceder a la web**
- Ve a [Google AI Studio](https://aistudio.google.com/app/apikey).

**b. Crear API Key**
- Selecciona la opción "Crear clave de API".
- Selecciona el proyecto de Google Cloud creado en el apartado anterior.
- Selecciona "Crear clave de API en un proyecto existente".

### 5. Configurar Variables de Entorno

**a. Crear el archivo `.env`:**
   - Renombra el archivo `.env.example` a `.env`.

**b. Rellenar el archivo `.env`:**

```ini
# .env
TOKEN_BOT=<tu_token_de_telegram>
SHEET_ID=<tu_id_de_google_sheets>
MY_USER_ID=<tu_id_de_usuario_de_telegram>
GEMINI_API_KEY=<tu_api_key_de_gemini>
```

-   `TOKEN_BOT`: Habla con [@BotFather](https://t.me/BotFather) en Telegram para crear un nuevo bot y obtener su token.
-   `SHEET_ID`: Es el ID de tu hoja de cálculo. Lo puedes encontrar en la URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`.
-   `GEMINI_API_KEY`: Inserta la API Key obtenida en el cuarto paso.
-   `MY_USER_ID`: Para obtener tu ID de usuario, primero ejecuta el bot (ver siguiente paso) y envíale el comando `/myid`. El bot te responderá con tu ID. Cópialo aquí y reinicia el bot.

## ▶️ Ejecutar el Bot

Una vez que toda la configuración esté completa, puedes iniciar el bot con el siguiente comando:

```bash
python main.py
```

Verás mensajes en la consola que indican que el bot se ha iniciado y conectado correctamente a los servicios.

## 💬 Uso

- **Enviar un gasto**: Simplemente escribe un mensaje como "25.50€ en una cena con amigos", graba un audio o envía una foto del ticket/gasto.
- **/start**: Muestra el mensaje de bienvenida.
- **/help**: Muestra un mensaje de ayuda.
- **/summary**: Muestra el resumen de gastos del mes actual.
- **/myid**: (Solo para configuración inicial) Muestra tu ID de usuario de Telegram. Se recomienda eliminar este comando de `main.py` después de configurar `MY_USER_ID`.
