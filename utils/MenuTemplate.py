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