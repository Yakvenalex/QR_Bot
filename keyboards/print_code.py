from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


keyboard_print = InlineKeyboardMarkup(row_width=1)
print_button = InlineKeyboardButton(text="Распечать код", callback_data="печать")
keyboard_print.add(print_button)

keyboard_print_list = ['печать']