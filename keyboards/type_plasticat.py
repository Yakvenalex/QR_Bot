from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


keyboard_type_plasticat = InlineKeyboardMarkup(row_width=3)
ppo_20_32_button = InlineKeyboardButton(text="ППО 20-32 черный", callback_data="ППО 20-32 черный")
ppo_20_28_button = InlineKeyboardButton(text="ППИ 20-28 неокрашенный", callback_data="ППИ 20-28 неокрашенный")
drugoe_button = InlineKeyboardButton(text="Другой", callback_data="Другой")
stop_button = InlineKeyboardButton(text="Заново", callback_data="Заново")
back_button = InlineKeyboardButton(text="Назад", callback_data="Назад")
keyboard_type_plasticat.add(ppo_20_32_button, ppo_20_28_button, drugoe_button, stop_button, back_button)

keyboard_type_plasticat_list = ['ППО 20-32 черный', 'ППИ 20-28 неокрашенный', 'Другой', 'Заново', 'Назад']