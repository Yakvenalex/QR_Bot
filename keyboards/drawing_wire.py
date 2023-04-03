from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_drawing_wire = InlineKeyboardMarkup(row_width=3)
pyatigorsk_button = InlineKeyboardButton(text="Пятигорск", callback_data="Пятигорск")
krim_button = InlineKeyboardButton(text="Крым", callback_data="Крым")
cold_button = InlineKeyboardButton(text="Прохладный", callback_data="Прохладный")
other_button = InlineKeyboardButton(text="Другое волочение", callback_data="Другое волочение")
stop_button = InlineKeyboardButton(text="Заново", callback_data="Заново")
back_button = InlineKeyboardButton(text="Назад", callback_data="Назад")
keyboard_drawing_wire.add(pyatigorsk_button, krim_button, cold_button, other_button, stop_button, back_button)

keyboard_drawing_wire_list = ['Пятигорск', 'Крым', 'Прохладный', 'Другое волочение', 'Заново', 'Назад']