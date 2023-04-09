from aiogram import types, Dispatcher
from create_bot import bot, AcceptState
from aiogram.dispatcher import FSMContext
from keyboards import (keyboard_type_product, keyboard_type_product_list, keyboard_supplier_plasticat, keyboard_supplier_wire)


async def handle_start(message: types.Message):
    await bot.send_message(message.from_user.id, f'Привет, {message.from_user.full_name}! Чем сегодня могу быть полезен?')


async def generate_qr(message: types.Message):
    await message.answer('Выберите тип продукта:', reply_markup=keyboard_type_product)
    await AcceptState.type_product.set()


async def restart_fsm(message: types.Message, state: FSMContext = None):
    await bot.send_message(message.from_user.id, 'машина состояний сброшена - делай что хочешь😏')
    if state:
        await state.finish()



async def type_product(callback_query: types.CallbackQuery, state: FSMContext):
    type_product = callback_query.data
    await bot.answer_callback_query(callback_query.id, text=f"Вы выбрали {type_product}")
    await state.update_data(type_product=type_product)
    data = await state.get_data()
    if data['type_product'] == 'Пластикат':
        await bot.send_message(callback_query.from_user.id, 'Выберите производителя пластиката:', reply_markup=keyboard_supplier_plasticat)
        await AcceptState.supplier_plasticat.set()
    elif data['type_product'] == 'Проволока':
        await bot.send_message(callback_query.from_user.id, 'Выберите производителя проволоки:',
                               reply_markup=keyboard_supplier_wire)
        await AcceptState.supplier_wire.set()
    elif data['type_product'] == 'Другое':
        await bot.send_message(callback_query.from_user.id, "Введите свое значение:")
        await AcceptState.enter_value.set()
    else:
        await bot.send_message(callback_query.from_user.id, 'Завершаю анкету')
        await state.finish()


def register_handlers_client_main(dp: Dispatcher):
    dp.register_message_handler(handle_start, commands=['start'])
    dp.register_message_handler(restart_fsm, commands=['restart_fsm'],  state='*')
    dp.register_message_handler(generate_qr, commands=['accept_materials'])
    dp.register_callback_query_handler(type_product, state=AcceptState.type_product)