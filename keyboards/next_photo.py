from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


keyboard_next_photo = InlineKeyboardMarkup(row_width=2)
button_more_photo = InlineKeyboardButton('Ещё фото', callback_data='more_photo')
button_calculate = InlineKeyboardButton('Посчитать', callback_data='calculate')
keyboard_next_photo.add(button_more_photo, button_calculate)