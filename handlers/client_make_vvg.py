from aiogram import types, Dispatcher
from create_bot import bot, AcceptState, dp
from aiogram.dispatcher import FSMContext
from keyboards import keyboard_create_defect, keyboard_type_vvg, keyboard_count_round, keyboard_yes_no, \
    keyboard_sec_round_vvg, keyboard_type_wire
from qr_scaner import read_qr_code_async
import os


@dp.message_handler(commands=['make_vvg'])
async def make_vvg_start(message: types.Message):
    await message.answer('Выберите из списка по форме:', reply_markup=keyboard_type_vvg)
    await AcceptState.type_vvg.set()


async def stop_script(call_id, user_id, state=AcceptState.type_vvg.set()):
    await bot.answer_callback_query(call_id, text="Возвращаюсь на начало скрипта")
    await bot.send_message(user_id, 'Выберите из списка по форме:',
                           reply_markup=keyboard_type_vvg)
    await state


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


@dp.callback_query_handler(state=AcceptState.type_vvg)
async def process_type_vvg(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'Круглый':
        await state.update_data(wire=callback_query.data)
        await bot.send_message(callback_query.from_user.id, 'Выберите кол-во жил для круглого:',
                               reply_markup=keyboard_count_round)
        await AcceptState.count_round_vvg.set()
    elif callback_query.data == 'Заново':
        await stop_script(callback_query.id, callback_query.from_user.id)
    else:
        await bot.send_message(callback_query.from_user.id, 'блок в разработке. Оставнавливаю сценарий')
        await state.finish()


@dp.callback_query_handler(state=AcceptState.count_round_vvg)
async def process_section_round(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'Заново':
        await stop_script(callback_query.id, callback_query.from_user.id)
    else:
        await state.update_data(count_round=callback_query.data)
        await bot.send_message(callback_query.from_user.id, 'Выберите сечение:', reply_markup=keyboard_sec_round_vvg)
        await AcceptState.section_vein_round.set()


@dp.callback_query_handler(state=AcceptState.section_vein_round)
async def process_round_vein(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'Заново':
        await stop_script(callback_query.id, callback_query.from_user.id)
    else:
        user_id = callback_query.from_user.id
        await state.update_data(vein_round=callback_query.data)
        await bot.send_message(user_id, 'Выбирите сечение, которое будет участвовать в проверке:',
                               reply_markup=keyboard_type_wire)
        await AcceptState.section_vein_round_check.set()


@dp.callback_query_handler(state=AcceptState.section_vein_round_check)
async def process_round_section_vvg(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'Заново':
        await stop_script(callback_query.id, callback_query.from_user.id)
    else:
        await state.update_data(section_vein_round_check=callback_query.data)
        await bot.send_message(callback_query.from_user.id, "Укажите метраж:")
        await AcceptState.metr_vvg_round.set()


@dp.message_handler(state=AcceptState.metr_vvg_round)
async def process_metr_vvg(message: types.Message, state: FSMContext):
    await state.update_data(metr=message.text)
    await bot.send_message(message.from_user.id, f'Отправьте мне фото QR-кода заготовки.')
    await AcceptState.photo_vvg.set()


@dp.message_handler(content_types=['photo', 'document'], state=AcceptState.photo_vvg)
async def process_photo_vvg(message: types.Message, state: FSMContext):
    if message.photo or message.document and 'image' in message.document.mime_type:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        data = await state.get_data()
        info = await handle_photos_and_documents_id(file_id, message, state)
        await bot.send_message(message.from_user.id, f'{info} -- {data}', reply_markup=keyboard_yes_no)
    else:
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptState.photo_vvg.set()


@dp.callback_query_handler(state=AcceptState.yes_vvg_round)
async def firs_yes_vvg(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'ДА':
        await bot.answer_callback_query(callback_query.id, text=f"ДА!")
        await bot.send_message(callback_query.from_user.id, 'Укажите результат работы',
                               reply_markup=keyboard_create_defect)
        await AcceptState.result_create.set()
        await state.finish()
    else:
        await bot.answer_callback_query(callback_query.id, text=f"НЕТ!")
        await AcceptState.restart_round_vvg.set()
