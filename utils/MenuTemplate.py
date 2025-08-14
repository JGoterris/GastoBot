from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.Routes import Routes

class MenuTemplate:
    @staticmethod
    def basic_menu():
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="✅ Aceptar", callback_data=Routes.ACEPTAR)
            ],
            [
                InlineKeyboardButton(text="✏️ Modificar", callback_data=Routes.MODIFICAR)
            ]
        ])

    @staticmethod
    def parameters_menu():
        return InlineKeyboardMarkup([
            [ InlineKeyboardButton(text="👕 Establecimiento", callback_data=Routes.MODIFICAR_ESTABLECIMIENTO) ],
            [ InlineKeyboardButton(text="💶 Importe", callback_data=Routes.MODIFICAR_IMPORTE) ],
            [ InlineKeyboardButton(text="📝 Descripción", callback_data=Routes.MODIFICAR_DESCRIPCION) ],
            [ InlineKeyboardButton(text="📅 Fecha", callback_data=Routes.MODIFICAR_FECHA) ],
            [ InlineKeyboardButton(text="🏷️ Categoría", callback_data=Routes.MODIFICAR_CATEGORIA) ],
            [ InlineKeyboardButton(text="✅ Aceptar", callback_data=Routes.ACEPTAR) ]
        ])
    
    def volver_atras_a_modificaciones():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Volver", callback_data=Routes.ATRAS_MODIFICACIONES)]
        ])