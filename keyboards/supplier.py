from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_supplier = InlineKeyboardMarkup(row_width=3)
inetcom_button = InlineKeyboardButton(text="Инетком", callback_data="Инетком")
varez_button = InlineKeyboardButton(text="Варез", callback_data="Варез")
other_button = InlineKeyboardButton(text="Другое", callback_data="Другое")
stop_button = InlineKeyboardButton(text="Заново", callback_data="Заново")
keyboard_supplier.add(inetcom_button, varez_button, other_button, stop_button)

keyboard_supplier_list = ['Инетком', 'Варез', 'Другое', 'Заново']