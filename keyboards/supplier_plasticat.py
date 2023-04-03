from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_supplier_plasticat = InlineKeyboardMarkup(row_width=3)
inetcom_button = InlineKeyboardButton(text='АО "ХЕМКОР"', callback_data='АО "ХЕМКОР"')
varez_button = InlineKeyboardButton(text="Варез", callback_data="Варез")
other_button = InlineKeyboardButton(text="Другое", callback_data="Другое")
stop_button = InlineKeyboardButton(text="Заново", callback_data="Заново")
keyboard_supplier_plasticat.add(inetcom_button, varez_button, other_button, stop_button)

keyboard_supplier_plasticat_list = ['АО "ХЕМКОР"', 'Варез', 'Другое', 'Заново']

