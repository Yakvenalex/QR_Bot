from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_color_pv = InlineKeyboardMarkup(row_width=3)
white_button = InlineKeyboardButton(text="бел.", callback_data="бел.")
blue_button = InlineKeyboardButton(text="син.", callback_data="син.")
gz_button = InlineKeyboardButton(text="ж/з", callback_data="ж/з")
red_button = InlineKeyboardButton(text="красн.", callback_data="красн.")
yellou_button = InlineKeyboardButton(text="желт.", callback_data="желт.")
green_button = InlineKeyboardButton(text="зелен.", callback_data="зелен.")
stop_button = InlineKeyboardButton(text="Заново", callback_data="Заново")
keyboard_color_pv.add(white_button, blue_button, gz_button, red_button, yellou_button, green_button, stop_button)

keyboard_color_pv_list = ['бел.', 'син.', 'ж/з', 'красн.', 'желт.', 'зелен.', 'Заново']