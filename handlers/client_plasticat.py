from aiogram import types, Dispatcher
from create_bot import bot, AcceptState
from aiogram.dispatcher import FSMContext
from get_qr import (get_id, get_date_now, generate_qr_code, get_data_to_db, write_to_db, create_data_to_write_in_qr,
                    create_data_to_send, find_user_descript)
from aiogram.types import ParseMode
from keyboards import (
    keyboard_type_plasticat, keyboard_type_plasticat_list, keyboard_supplier_plasticat_list,
    keyboard_manufacturer, keyboard_manufacturer_list, keyboard_yes_no, keyboard_type_yes_no_list,
    keyboard_type_product, keyboard_supplier_plasticat, keyboard_print
)
from async_funck import send_qr_code


async def stop_product(user_id):
    await bot.send_message(user_id, 'Выберите тип продукта:', reply_markup=keyboard_type_product)
    await AcceptState.type_product.set()


async def process_supplier(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Заново':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на начало скрипта")
        await state.finish()
        await stop_product(user_id)
    else:
        supplier = callback_query.data
        await bot.answer_callback_query(callback_query.id, text=f"Вы выбрали {supplier}")
        await state.update_data(supplier=supplier)
        await bot.send_message(user_id, 'Выберите изготовителя пластиката:',
                               reply_markup=keyboard_manufacturer)
        await AcceptState.manufacturer_plasticat.set()


async def process_manufacturer(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Заново':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на начало скрипта")
        await state.finish()
        await stop_product(user_id)
    elif callback_query.data == 'Назад':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на шаг назад")
        await bot.send_message(callback_query.from_user.id, 'Выберите производителя пластиката:',
                               reply_markup=keyboard_supplier_plasticat)
        await AcceptState.supplier_plasticat.set()
    else:
        manufacturer = callback_query.data
        await bot.answer_callback_query(callback_query.id, text=f"Вы выбрали {manufacturer}")
        await state.update_data(manufacturer=manufacturer)
        await bot.send_message(callback_query.from_user.id, 'Укажите тип пластиката:',
                               reply_markup=keyboard_type_plasticat)
        await AcceptState.plasticat.set()


# блок работы с пластикатом
async def process_plasticat(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Другой':
        await bot.send_message(user_id, 'Введите тип пластика:')
        await AcceptState.waiting_for_plasticat.set()
    elif callback_query.data == 'Заново':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на начало скрипта")
        await state.finish()
        await stop_product(user_id)
    elif callback_query.data == 'Назад':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на шаг назад")
        await bot.send_message(user_id, 'Выберите изготовителя пластиката:', reply_markup=keyboard_manufacturer)
        await AcceptState.manufacturer_plasticat.set()
    else:
        plasticat = callback_query.data
        await bot.answer_callback_query(callback_query.id, text=f"Вы выбрали {plasticat}")
        await state.update_data(plasticat=plasticat)
        await bot.send_message(user_id, 'Количество (кг):')
        await AcceptState.volume_plasticat.set()


async def process_plasticat_input(message: types.Message, state: FSMContext):
    plasticat = message.text
    await state.update_data(plasticat=plasticat)
    await bot.send_message(message.from_user.id, 'Количество (кг):')
    await AcceptState.volume_plasticat.set()


def dict_to_string(my_dict):
    result = ""
    for key, value in my_dict.items():
        result += f"{key}: {value}\n"
    return result


async def process_end_plasticat(message: types.Message, state: FSMContext):
    volume = message.text
    user_id = message.from_user.id
    await state.update_data(user_id=user_id)
    await state.update_data(volume=volume)
    data = await state.get_data()

    await bot.send_message(message.from_user.id, dict_to_string(create_data_to_send(data)))
    await state.update_data(id=get_id())
    await state.update_data(date_now=get_date_now())

    await message.answer('Все ли верно?', reply_markup=keyboard_yes_no)
    await AcceptState.check.set()


async def check(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'ДА':
        await bot.answer_callback_query(callback_query.id, text=f"ДА!")
        data = await state.get_data()
        await bot.send_message(user_id, dict_to_string(create_data_to_send(data)), reply_markup=keyboard_print)
        await AcceptState.print_plasticat.set()
    else:
        await bot.answer_callback_query(callback_query.id, text=f"НЕТ!")
        await bot.send_message(callback_query.from_user.id, 'Выберите тип продукта:',
                               reply_markup=keyboard_type_product)
        await AcceptState.type_product.set()


async def print_plasticat(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'печать':
        await bot.answer_callback_query(callback_query.id, text=f"сейчас я распечатаю QR-код")
        await state.update_data(user_id=str(user_id))
        await state.update_data(user_descript=find_user_descript(str(user_id)))
        data = await state.get_data()
        data_db = get_data_to_db(data)
        write_to_db(data_db)
        data_dict = create_data_to_write_in_qr(data)
        data_send = generate_qr_code(data_dict)
        await send_qr_code(data['user_id'], data_send)
        await state.finish()


def register_handlers_client_plasticat(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(process_supplier, state=AcceptState.supplier_plasticat)
    dp.register_callback_query_handler(process_manufacturer, state=AcceptState.manufacturer_plasticat)
    dp.register_callback_query_handler(process_plasticat, state=AcceptState.plasticat)
    dp.register_message_handler(process_end_plasticat, state=AcceptState.volume_plasticat)
    dp.register_message_handler(process_plasticat_input, state=AcceptState.waiting_for_plasticat)
    dp.register_callback_query_handler(check, state=AcceptState.check)
    dp.register_callback_query_handler(print_plasticat, state=AcceptState.print_plasticat)
