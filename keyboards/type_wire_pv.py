from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_type_wire_pv = InlineKeyboardMarkup(row_width=3)
pr_1_72_button = InlineKeyboardButton(text="1,72", callback_data="1,72")
pr_1_34_button = InlineKeyboardButton(text="1,34", callback_data="1,34")
pr_2_19_button = InlineKeyboardButton(text="2,19", callback_data="2,19")
pr_2_67_button = InlineKeyboardButton(text="2,67", callback_data="2,67")
pr_3_48_button = InlineKeyboardButton(text="3,48", callback_data="3,48")
pr_3_5_button = InlineKeyboardButton(text="3,5", callback_data="3,5")
pr_4_4_button = InlineKeyboardButton(text="4,4", callback_data="4,4")
pr_oth_button = InlineKeyboardButton(text="Другой тип проволоки", callback_data="Другой тип проволоки")
keyboard_type_wire_pv.add(pr_1_72_button, pr_1_34_button, pr_2_19_button, pr_2_67_button, pr_3_48_button, pr_3_5_button,
                       pr_4_4_button, pr_oth_button)
keyboard_type_wire_pv_list = ['1,72', '1,34', '2,19', '2,67', '3,48', '3,5', '4,4', 'Другой тип проволоки']
