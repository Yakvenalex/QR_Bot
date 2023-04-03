from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_count_round = InlineKeyboardMarkup(row_width=3)
c1_button = InlineKeyboardButton(text="1", callback_data="1")
c2_button = InlineKeyboardButton(text="2", callback_data="2")
c3_button = InlineKeyboardButton(text="3", callback_data="3")
c4_button = InlineKeyboardButton(text="4", callback_data="4")
c5_button = InlineKeyboardButton(text="5", callback_data="5")
stop_button = InlineKeyboardButton(text="Заново", callback_data="Заново")
back_button = InlineKeyboardButton(text="Назад", callback_data="Назад")
keyboard_count_round.add(c1_button, c2_button, c3_button, c4_button, c5_button, stop_button, back_button)
keyboard_count_round_list = ['1', '2', '3', '4', '5', 'Заново', 'Назад']