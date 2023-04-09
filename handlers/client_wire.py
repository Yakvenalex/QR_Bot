from aiogram import types, Dispatcher
from create_bot import bot, AcceptState
from aiogram.dispatcher import FSMContext
from get_qr import get_id, get_date_now, generate_qr_code, get_data_to_db, write_to_db, create_data_to_write_in_qr, \
    create_data_to_send
from aiogram.types import ParseMode
from keyboards import keyboard_manufacturer_list_wire, keyboard_manufacturer_wire, keyboard_supplier_wire_list, \
    keyboard_type_wire_list, keyboard_type_wire, keyboard_yes_no, keyboard_type_yes_no_list, keyboard_type_product, \
    keyboard_drawing_wire_list, keyboard_drawing_wire, keyboard_supplier_wire, keyboard_print
from async_funck import send_qr_code

async def stop_product(user_id):
    await bot.send_message(user_id, 'Выберите тип продукта:', reply_markup=keyboard_type_product)
    await AcceptState.type_product.set()


async def process_supplier_wire(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Заново':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на начало скрипта")
        await state.finish()
        await stop_product(user_id)
    else:
        supplier = callback_query.data
        await state.update_data(supplier=supplier)
        await bot.send_message(callback_query.from_user.id, 'Выберите изготовителя проволоки:',
                               reply_markup=keyboard_manufacturer_wire)
        await AcceptState.manufacturer_wire.set()


async def process_manufacturer_wire(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Заново':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на начало скрипта")
        await state.finish()
        await stop_product(user_id)
    elif callback_query.data == 'Назад':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на шаг назад")
        await bot.send_message(callback_query.from_user.id, 'Выберите производителя проволоки:',
                               reply_markup=keyboard_supplier_wire)
        await AcceptState.supplier_wire.set()
    else:
        manufacturer = callback_query.data
        await state.update_data(manufacturer=manufacturer)
        await bot.send_message(callback_query.from_user.id, 'Волочение:', reply_markup=keyboard_drawing_wire)
        await AcceptState.drawing.set()


async def drawing(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Заново':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на начало скрипта")
        await state.finish()
        await stop_product(user_id)
    elif callback_query.data == 'Другое волочение':
        await bot.send_message(callback_query.from_user.id, 'Введите волочение:')
        await AcceptState.waiting_for_drawing.set()
    elif callback_query.data == 'Назад':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на шаг назад")
        await bot.send_message(callback_query.from_user.id, 'Выберите изготовителя проволоки:',
                               reply_markup=keyboard_manufacturer_wire)
        await AcceptState.manufacturer_wire.set()
    else:
        drawing = callback_query.data
        await state.update_data(drawing=drawing)
        await bot.send_message(callback_query.from_user.id, 'Выберите тип проволоки:', reply_markup=keyboard_type_wire)
        await AcceptState.wire.set()



async def process_drawing_input(message: types.Message, state: FSMContext):
    drawing = message.text
    await state.update_data(drawing=drawing)
    await bot.send_message(message.from_user.id, 'Выберите тип проволоки:', reply_markup=keyboard_type_wire)
    await AcceptState.wire.set()


async def process_wire(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Заново':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на начало скрипта")
        await state.finish()
        await stop_product(user_id)
    elif callback_query.data == 'Другой тип проволоки':
        await bot.send_message(callback_query.from_user.id, 'Введите тип проволоки:')
        await AcceptState.waiting_for_wire.set()
    elif callback_query.data == 'Назад':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на шаг назад")
        await bot.send_message(callback_query.from_user.id, 'Волочение:', reply_markup=keyboard_drawing_wire)
        await AcceptState.drawing.set()
    else:
        wire = callback_query.data
        await state.update_data(wire=wire)
        await bot.send_message(callback_query.from_user.id, 'Вес нетто:')
        await AcceptState.volume_wire.set()



async def process_wire_input(message: types.Message, state: FSMContext):
    wire = message.text
    await state.update_data(wire=wire)
    await bot.send_message(message.from_user.id, 'Объем:')
    await AcceptState.volume_wire.set()


async def volume_wire(message: types.Message, state: FSMContext):
    volume_wire = message.text
    await state.update_data(volume=volume_wire)
    await message.answer('Метраж:')
    await AcceptState.metr_wire.set()


def dict_to_string(my_dict):
    result = ""
    for key, value in my_dict.items():
        result += f"{key}: {value}\n"
    return result


async def process_end_wire(message: types.Message, state: FSMContext):
    metr = message.text
    user_id = message.from_user.id
    await state.update_data(user_id=user_id)
    await state.update_data(metr=metr)

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

async def print_wire(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'печать':
        await bot.answer_callback_query(callback_query.id, text=f"сейчас я распечатаю QR-код")
        data = await state.get_data()
        data_db = get_data_to_db(data)
        write_to_db(data_db)
        data_dict = create_data_to_write_in_qr(data)
        data_send = generate_qr_code(data_dict)
        await send_qr_code(data['user_id'], data_send)
        await state.finish()



def register_handlers_client_wire(dp: Dispatcher):
    dp.register_callback_query_handler(process_supplier_wire, lambda c: c.data in keyboard_supplier_wire_list,
                                       state=AcceptState.supplier_wire)
    dp.register_callback_query_handler(process_manufacturer_wire, lambda c: c.data in keyboard_manufacturer_list_wire,
                                       state=AcceptState.manufacturer_wire)
    dp.register_callback_query_handler(drawing, lambda c: c.data in keyboard_drawing_wire_list, state=AcceptState.drawing)
    dp.register_callback_query_handler(process_wire, lambda c: c.data in keyboard_type_wire_list,
                                       state=AcceptState.wire)
    dp.register_message_handler(volume_wire, state=AcceptState.volume_wire)
    dp.register_message_handler(process_end_wire, state=AcceptState.metr_wire)
    dp.register_message_handler(process_drawing_input, state=AcceptState.waiting_for_drawing)
    dp.register_message_handler(process_wire_input, state=AcceptState.waiting_for_wire)
    dp.register_callback_query_handler(check, lambda c: c.data in keyboard_type_yes_no_list, state=AcceptState.check)

