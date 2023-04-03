from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


keyboard_type_product = InlineKeyboardMarkup(row_width=3)
provolka_button = InlineKeyboardButton(text="Проволока", callback_data="Проволока")
plastikat_button = InlineKeyboardButton(text="Пластикат", callback_data="Пластикат")
drugoe_button = InlineKeyboardButton(text="Другое", callback_data="Другое")
keyboard_type_product.add(provolka_button, plastikat_button, drugoe_button)

keyboard_type_product_list = ['Проволока', 'Пластикат', 'Другое']