from aiogram import types, Dispatcher
from create_bot import bot, dp
from aiogram.dispatcher import FSMContext
from keyboards import keyboard_create_defect, keyboard_type_vvg, keyboard_count_round, keyboard_yes_no, \
    keyboard_sec_round_vvg, keyboard_type_wire, keyboard_type_rewind, keyboard_type_rewind_2, \
    keyboard_create_defect_tara, keyboard_print, keyboard_stop_tara
from qr_scaner import read_qr_code_async
import os
from async_funck import stop_script, step_back
from aiogram.dispatcher.filters.state import StatesGroup, State


class AcceptStateRewind(StatesGroup):
    tara_metr_create = State()
    check_start_stop = State()
    result_create_tara_print = State()
    result_create_tara = State()
    restart_round_vvg = State()
    result_create = State()
    yes_tara_1 = State()
    rewind_photo = State()
    tara_metr = State()
    type_rewind = State()
    type_rewind_2 = State()
    type_tara_rewind = State()


async def handle_photos_and_documents_id(file_id: str, message: types.Message, state: FSMContext):
    file = await bot.get_file(file_id)
    file_path = file.file_path
    photo_path = f"photos\photo_{file_id}.png"  # генерируем уникальное имя файла для сохранени
    await bot.download_file(file_path, photo_path)
    text = await read_qr_code_async(photo_path)
    text = text.split('\n')
    if 'Проволка' in text[0]:
        return text
    else:
        await bot.send_message(message.from_user.id, 'ошибка - завершаю скрипт')
        await state.finish()


@dp.message_handler(commands=['rewind'])
async def make_vvg_start(message: types.Message):
    await message.answer('Выберите из списка по типу операции:', reply_markup=keyboard_type_rewind)
    await AcceptStateRewind.type_rewind.set()


@dp.callback_query_handler(state=AcceptStateRewind.type_rewind)
async def process_type_remind(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'Перемотка':
        await state.update_data(wire=callback_query.data)
        await bot.send_message(callback_query.from_user.id, 'Что перематываем:',
                               reply_markup=keyboard_type_rewind_2)
        await AcceptStateRewind.type_rewind_2.set()
    else:
        await bot.send_message(callback_query.from_user.id, 'блок в разработке. Оставнавливаю сценарий')
        await state.finish()


@dp.callback_query_handler(state=AcceptStateRewind.type_rewind_2)
async def process_type_remind_2(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'other_tara':
        await state.update_data(wire=callback_query.data)
        await bot.send_message(callback_query.from_user.id, 'Выбирете размер:',
                               reply_markup=keyboard_type_wire)
        await AcceptStateRewind.type_tara_rewind.set()
    else:
        await bot.send_message(callback_query.from_user.id, 'блок в разработке. Оставнавливаю сценарий')
        await state.finish()


@dp.callback_query_handler(state=AcceptStateRewind.type_tara_rewind)
async def process_type_tara(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(tara=callback_query.data)
    await bot.send_message(callback_query.from_user.id, 'Укажите метраж:')
    await AcceptStateRewind.tara_metr.set()


@dp.message_handler(state=AcceptStateRewind.tara_metr)
async def hand_section_vein_round(message: types.Message, state: FSMContext):
    await state.update_data(metr=message.text)
    await bot.send_message(message.from_user.id, 'Сканируйте код:')
    await AcceptStateRewind.rewind_photo.set()


@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.DOCUMENT],
                    state=AcceptStateRewind.rewind_photo)
async def process_photo_vvg(message: types.Message, state: FSMContext):
    if message.content_type == types.ContentType.PHOTO:
        file_id = message.photo[-1].file_id
    elif message.content_type == types.ContentType.DOCUMENT and message.document.mime_type.startswith('image/'):
        file_id = message.document.file_id
    else:
        file_id = ''
        await bot.send_message(message.from_user.id, 'Пришлите фото QR-кода')
        await AcceptStateRewind.rewind_photo.set()

    data = await state.get_data()
    info = await handle_photos_and_documents_id(file_id, message, state)
    new_text = f'Вы собираетесь перемотать проволоку {info[0].replace("Проволка: ", "")}  {info[2]} верно?'
    await state.update_data(metr=info[2].replace('м', ''))
    await state.update_data(old_sec=info[0].replace("Проволка: ", ""))
    await bot.send_message(message.from_user.id, new_text, reply_markup=keyboard_yes_no)
    await AcceptStateRewind.yes_tara_1.set()


@dp.callback_query_handler(state=AcceptStateRewind.yes_tara_1)
async def firs_yes_tara(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'ДА':
        await bot.answer_callback_query(callback_query.id, text=f"ДА!")
        await bot.send_message(callback_query.from_user.id, 'Укажите результат работы',
                               reply_markup=keyboard_create_defect_tara)
        await AcceptStateRewind.result_create_tara.set()
    else:
        await bot.answer_callback_query(callback_query.id, text=f"НЕТ!")
        await AcceptStateRewind.restart_round_vvg.set()


@dp.callback_query_handler(state=AcceptStateRewind.result_create_tara)
async def result_create_tara(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'Перемотка':
        await bot.answer_callback_query(callback_query.id, text=f"Перемотка!")
        await bot.send_message(callback_query.from_user.id, 'Укажите метраж: ')
        await AcceptStateRewind.tara_metr_create.set()
    else:
        await bot.answer_callback_query(callback_query.id, text=f"НЕТ!")
        await AcceptStateRewind.restart_round_vvg.set()


@dp.message_handler(state=AcceptStateRewind.tara_metr_create)
async def hand_section_vein_round(message: types.Message, state: FSMContext):
    await state.update_data(metr_new=message.text)
    data = await state.get_data()
    new_text = f'Вы перемотали проволоку {data["old_sec"]}  {data["metr_new"]}м верно?'
    await bot.send_message(message.from_user.id, new_text, reply_markup=keyboard_yes_no)
    await AcceptStateRewind.result_create_tara_print.set()


@dp.callback_query_handler(state=AcceptStateRewind.result_create_tara_print)
async def result_create_tara(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, 'Сейчас начнется печать кода', reply_markup=keyboard_stop_tara)
    await AcceptStateRewind.check_start_stop.set()


@dp.callback_query_handler(state=AcceptStateRewind.check_start_stop)
async def result_create_tara(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'add':
        await bot.send_message(callback_query.from_user.id, 'Выберите из списка по типу операции:',
                               reply_markup=keyboard_type_rewind)
        await AcceptStateRewind.type_rewind.set()
    else:
        await bot.send_message(callback_query.from_user.id, 'Скрипт завершен, можете воспользоваться другими функциями '
                                                            'бота')
        await state.finish()
