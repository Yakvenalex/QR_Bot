from aiogram import types, Dispatcher
from create_bot import bot, AcceptState
from aiogram.dispatcher import FSMContext
from get_qr import get_id, get_date_now, generate_qr_code, get_data_to_db, write_to_db, create_data_to_write_in_qr
from aiogram.types import ParseMode
from async_funck import send_qr_code


async def process_wire_2(message: types.Message, state: FSMContext):
    enter_value = message.text
    await state.update_data(enter_value=enter_value)
    await message.answer('Волочение:')
    await AcceptState.drawing.set()


async def drawing_2(message: types.Message, state: FSMContext):
    drawing = message.text
    await state.update_data(drawing=drawing)
    await message.answer('Количество (кг):')
    await AcceptState.volume_wire.set()


async def volume_wire_2(message: types.Message, state: FSMContext):
    volume_wire = message.text
    await state.update_data(volume=volume_wire)
    await message.answer('Метраж:')
    await AcceptState.metr_wire.set()


async def process_end_wire_2(message: types.Message, state: FSMContext):
    metr = message.text
    user_id = message.from_user.id
    await state.update_data(metr=metr)
    await state.update_data(id=get_id())
    await state.update_data(date_now=get_date_now())
    data = await state.get_data()

    data_db = get_data_to_db(data)
    write_to_db(data_db)
    data_dict = create_data_to_write_in_qr(data)
    data_send = generate_qr_code(data_dict)
    await send_qr_code(user_id, data_send)
    await state.finish()


def register_handlers_client_other(dp: Dispatcher):
    dp.register_message_handler(process_wire_2, state=AcceptState.enter_value)
    dp.register_message_handler(drawing_2, state=AcceptState.drawing)
    dp.register_message_handler(volume_wire_2, state=AcceptState.volume_wire)
    dp.register_message_handler(process_end_wire_2, state=AcceptState.metr_wire)