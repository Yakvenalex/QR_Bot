from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_yes_no = InlineKeyboardMarkup(row_width=2)
yes_button = InlineKeyboardButton(text="ДА", callback_data="ДА")
no_button = InlineKeyboardButton(text="НЕТ", callback_data="НЕТ")
keyboard_yes_no.add(yes_button, no_button)

keyboard_type_yes_no_list = ['ДА', 'НЕТ']