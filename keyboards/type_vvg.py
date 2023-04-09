from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_type_vvg = InlineKeyboardMarkup(row_width=2)
flat_button = InlineKeyboardButton(text="Плоский", callback_data="Плоский")
round_button = InlineKeyboardButton(text="Круглый", callback_data="Круглый")
keyboard_type_vvg.add(flat_button, round_button)
keyboard_type_vvg_list = ['Плоский', 'Круглый']