from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_count_twist = InlineKeyboardMarkup(row_width=2)
c2_button = InlineKeyboardButton(text="2", callback_data="2")
c3_button = InlineKeyboardButton(text="3", callback_data="3")
c4_button = InlineKeyboardButton(text="4", callback_data="4")
c5_button = InlineKeyboardButton(text="5", callback_data="5")
keyboard_count_twist.add(c2_button, c3_button, c4_button, c5_button)