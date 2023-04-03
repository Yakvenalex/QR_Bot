from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


keyboard_manufacturer_wire = InlineKeyboardMarkup(row_width=3)
izg1_button = InlineKeyboardButton(text="Изготовитель1", callback_data="Изготовитель1")
izg2_button = InlineKeyboardButton(text="Изготовитель2", callback_data="Изготовитель2")
other_izg_button = InlineKeyboardButton(text="ДругойИзготовитель", callback_data="ДругойИзготовитель")
stop_button = InlineKeyboardButton(text="Заново", callback_data="Заново")
back_button = InlineKeyboardButton(text="Назад", callback_data="Назад")
keyboard_manufacturer_wire.add(izg1_button, izg2_button, other_izg_button, stop_button, back_button)

keyboard_manufacturer_list_wire = ['Изготовитель1', 'Изготовитель2', 'ДругойИзготовитель', 'Заново', 'Назад']