from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_create_defect = InlineKeyboardMarkup(row_width=2)
create_button = InlineKeyboardButton(text="Изготовлено", callback_data="Изготовлено")
defect_button = InlineKeyboardButton(text="Брак", callback_data="Брак")
accident_button = InlineKeyboardButton(text="Авария", callback_data="Авария")
keyboard_create_defect.add(create_button, defect_button, accident_button)

keyboard_create_defect_list = ['Изготовлено', 'Брак', 'Авария']