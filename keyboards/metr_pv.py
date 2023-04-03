from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_metr_pv = InlineKeyboardMarkup(row_width=2)
all_button = InlineKeyboardButton(text="Весь", callback_data="Весь")
hand_button = InlineKeyboardButton(text="Указать", callback_data="Указать")
stop_button = InlineKeyboardButton(text="Заново", callback_data="Заново")
back_button = InlineKeyboardButton(text="Назад", callback_data="Назад")
keyboard_metr_pv.add(all_button, hand_button, stop_button, back_button)

keyboard_metr_pv_list = ['Весь', 'Указать', 'Заново', 'Назад']