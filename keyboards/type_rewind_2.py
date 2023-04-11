from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_type_rewind_2 = InlineKeyboardMarkup(row_width=3)
tara_button = InlineKeyboardButton(text="На другую тару", callback_data="other_tara")
welding_button = InlineKeyboardButton(text="Cварка остатков", callback_data="welding")
rewind_puv_button = InlineKeyboardButton(text="Перемотка ПУВ", callback_data="rewind_puv")
keyboard_type_rewind_2.add(tara_button, welding_button, rewind_puv_button)