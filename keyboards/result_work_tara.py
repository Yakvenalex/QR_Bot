from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_create_defect_tara = InlineKeyboardMarkup(row_width=2)
create_button = InlineKeyboardButton(text="Перемотка", callback_data="Перемотка")
defect_button = InlineKeyboardButton(text="Брак", callback_data="Брак")
keyboard_create_defect_tara.add(create_button, defect_button)

keyboard_create_defect_list = ['Изготовлено', 'Брак', 'Авария']