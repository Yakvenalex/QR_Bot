from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_supplier_wire = InlineKeyboardMarkup(row_width=3)
inetcom_button = InlineKeyboardButton(text="ИнеткомПЛ", callback_data="ИнеткомПЛ")
varez_button = InlineKeyboardButton(text="ВарезПЛ", callback_data="ВарезПЛ")
other_button = InlineKeyboardButton(text="ДругоеПЛ", callback_data="ДругоеПЛ")
stop_button = InlineKeyboardButton(text="Заново", callback_data="Заново")
keyboard_supplier_wire.add(inetcom_button, varez_button, other_button, stop_button)

keyboard_supplier_wire_list = ['ИнеткомПЛ', 'ВарезПЛ', 'ДругоеПЛ', 'Заново']