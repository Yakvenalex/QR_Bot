from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_type_rewind = InlineKeyboardMarkup(row_width=3)
rew_button = InlineKeyboardButton(text="Перемотка", callback_data="Перемотка")
puv_button = InlineKeyboardButton(text="Чистка ПУВ", callback_data="Чистка ПУВ")
keyboard_type_rewind.add(rew_button, puv_button)