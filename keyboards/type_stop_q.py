from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_stop_tara = InlineKeyboardMarkup(row_width=3)
add_button = InlineKeyboardButton(text="Добавить еще проволоку", callback_data="add")
stop_button = InlineKeyboardButton(text="Завершить скрипт", callback_data="stop")
keyboard_stop_tara.add(add_button, stop_button)