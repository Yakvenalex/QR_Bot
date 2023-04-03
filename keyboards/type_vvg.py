from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_type_vvg = InlineKeyboardMarkup(row_width=2)
flat_button = InlineKeyboardButton(text="Плоский", callback_data="Плоский")
round_button = InlineKeyboardButton(text="Круглый", callback_data="Круглый")
stop_button = InlineKeyboardButton(text="Заново", callback_data="Заново")
keyboard_type_vvg.add(flat_button, round_button, stop_button)
keyboard_type_vvg_list = ['Плоский', 'Круглый', 'Заново']