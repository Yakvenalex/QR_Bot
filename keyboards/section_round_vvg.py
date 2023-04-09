from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_sec_round_vvg = InlineKeyboardMarkup(row_width=3)
sec_1_5_button = InlineKeyboardButton(text="1,5", callback_data="1,5")
sec_2_5_button = InlineKeyboardButton(text="2,5", callback_data="2,5")
sec_4_button = InlineKeyboardButton(text="4", callback_data="4")
sec_6_button = InlineKeyboardButton(text="6", callback_data="6")
sec_10_button = InlineKeyboardButton(text="10", callback_data="10")
sec_16_button = InlineKeyboardButton(text="16", callback_data="16")
stop_button = InlineKeyboardButton(text="Заново", callback_data="Заново")
back_button = InlineKeyboardButton(text="Назад", callback_data="Назад")
hand_button = InlineKeyboardButton(text="Ввести", callback_data="enter")
keyboard_sec_round_vvg.add(sec_1_5_button, sec_2_5_button, sec_4_button, sec_6_button, sec_10_button, sec_16_button,
                           stop_button, back_button, hand_button)
keyboard_sec_round_vvg_list = ['1,5', '2,5', '4', '6', '10', '16', 'Заново', 'Назад']
