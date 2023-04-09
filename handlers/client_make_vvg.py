from aiogram import types, Dispatcher
from create_bot import bot, AcceptState
from aiogram.dispatcher import FSMContext
from keyboards import (keyboard_create_defect, keyboard_type_vvg, keyboard_count_round, keyboard_yes_no)
from get_qr import (get_operation_id, get_date_now, generate_qr_code, get_data_to_db_operation, write_to_db_operation,
                    create_data_to_write_in_qr, create_data_to_send, find_user_descript)
from qr_scaner import read_qr_code_async
import os
from async_funck import send_qr_code, check_color, check_wire


async def make_vvg_start(message: types.Message):
    await message.answer('Выберите из списка по форме:', reply_markup=keyboard_type_vvg)
    await AcceptState.type_vvg.set()


async def stop_make_vvg(user_id):
    await bot.send_message(user_id, 'Выберите из списка по форме:',
                           reply_markup=keyboard_type_vvg)
    await AcceptState.type_vvg.set()


async def handle_photos_and_documents_id(file_id: str, message: types.Message, state: FSMContext):
    file_path = await bot.get_file(file_id)
    file_name = file_path.file_path.split('/')[-1]
    await bot.download_file(file_path.file_path, os.path.join(os.getcwd(), 'photos', file_name))

    text = await read_qr_code_async(file_name)
    text = text.split('\n')

    if text[0] == 'Изготовить: Скрутка':
        return text
    else:
        await bot.send_message(message.from_user.id, 'ошибка - завершаю скрипт')
        await state.finish()


async def process_type_vvg(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Круглый':
        wire = callback_query.data
        await state.update_data(wire=wire)
        await bot.send_message(user_id, 'Выберите кол-во жил для круглого:', reply_markup=keyboard_count_round)
        await AcceptState.section_vvg.set()
    else:
        await bot.send_message(user_id, 'блок в разработке. Оставнавливаю сценарий')
        await state.finish()


async def process_round_section_vvg(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'Заново':
        await bot.answer_callback_query(callback_query.id, text=f"Возвращаюсь на начало скрипта")
        await stop_make_vvg(user_id)
    else:
        sec_round = callback_query.data
        await state.update_data(section_vvg=sec_round)
        await bot.send_message(user_id, 'Укажите метраж:')
        await AcceptState.metr_vvg.set()








async def process_metr_vvg(message: types.Message, state: FSMContext):
    metr = message.text
    await state.update_data(metr=metr)
    await bot.send_message(message.from_user.id, f'Отправьте мне фото QR-кода заготовки.')
    await AcceptState.photo_vvg.set()


async def process_photo_vvg(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        data = await state.get_data()
        info = await handle_photos_and_documents_id(file_id, message, state)
        await bot.send_message(message.from_user.id, f'{info} -- {data}', reply_markup=keyboard_yes_no)
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_vvg.set()


async def firs_yes_vvg(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'ДА':
        await bot.answer_callback_query(callback_query.id, text=f"ДА!")
        await bot.send_message(user_id, 'Укажите результат работы', reply_markup=keyboard_create_defect)
        await AcceptState.result_create.set()
        await state.finish()
    else:
        await bot.answer_callback_query(callback_query.id, text=f"НЕТ!")
        await stop_make_vvg(user_id)


def register_handlers_client_make_vvg(dp: Dispatcher):
    dp.register_message_handler(make_vvg_start, commands=['make_vvg'])
    dp.register_callback_query_handler(process_type_vvg, state=AcceptState.type_vvg)
    dp.register_callback_query_handler(process_round_section_vvg, state=AcceptState.section_vvg)
    dp.register_message_handler(process_metr_vvg, state=AcceptState.metr_vvg)
    dp.register_message_handler(process_photo_vvg, content_types=['photo', 'document'], state=AcceptState.photo_vvg)